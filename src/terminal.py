import string
import time
import re
import math
import urllib3
from .logger import *
from pynput import keyboard
from xml.etree import ElementTree as ET


ENTRY_TAG = "{http://www.w3.org/2005/Atom}entry"
DATE_TAG = "{http://www.w3.org/2005/Atom}published"
TITLE_TAG = "{http://www.w3.org/2005/Atom}title"
ABSTRACT_TAG = "{http://www.w3.org/2005/Atom}summary"
AUTHOR_TAG = "{http://www.w3.org/2005/Atom}author"
ARXIV_URL = "http://export.arxiv.org/api/query?search_query=cat:cs.CV&sortBy=lastUpdatedDate&sortOrder=descending&max_results=100"
class Console(object):
    logger = None
    pool = None
    def __init__(self, name="console", log_dir="./log"):
        self.name = name
        self.log_dir = log_dir
        self.logger = ClassicLogger(name=self.name, to_dir=self.log_dir, to_file=True)
        self.data = [{
            "title": "An article {}".format(i),
            "date": time.strftime("%Y-%m-%d"),
            "authors": [""],
            "abstract": "".join(["Abstract"]*50)
            } for i in range(100)]
        self.update()
        self.current_row = 1
        self.current_min = 0
        self.widths = [30, 15, 35, 70]
        self.pool = urllib3.PoolManager(100, block=True)

    def update(self, interval=3*60*60):
        # while True:
            new_data = []
            try:
                resp = self.pool.request("GET", ARXIV_URL)
                xml_str = resp.data.decode("utf-8")
                root = ET.fromstring(xml_str)
                children = root.getchildren()
                entries = []
                for child in children:
                    if child.tag == ENTRY_TAG:
                        entries.append(child)
                 
                for entry in entries:
                    obj = {"title": "", "authors": [], "date": "", "abstract": ""}
                    children = entry.getchildren()
                    for child in children:
                        if child.tag == TITLE_TAG:
                            obj["title"] = child.text
                        elif child.tag == DATE_TAG:
                            obj["date"] = child.text
                        elif child.tag == ABSTRACT_TAG:
                            obj["abstract"] = child.text
                        elif child.tag == AUTHOR_TAG:
                            obj["authors"].append(child.getchildren()[0].text)
                    new_data.append(obj)
                resp.release_conn()
            except Exception as e:
                self.logger.warn(e)
            self.data = new_data

    def print(self):
        titles = ["Title", "Date", "Author(s)", "Abstract"]
        self.printHeader(titles, self.widths)
        rows = [[d["title"], d["date"], ", ".join(d["authors"])] for d in self.data[self.current_min:self.current_min+30]]
        record = self.data[self.current_min+self.current_row]
        longtext = "Title: {}, Abstract: {}".format(record["title"], record["abstract"])
        self.printBody(rows, self.widths, longtext)

    def clearScreen(self):
        print("\033[2J\033[0;0H{}\n\033[4mKey bindings:\nUp/down arrows: move up and down inside the list\tLeft arrow: get latest 100 articles from ArXiV server\tEsc key: to exit from this program\033[m".format(
              time.strftime("%Y-%m-%d %H:%M:%S%z%Z")))

    def printHeader(self, titles, widths):
        parts = [self.formatLongLine(titles[i], widths[i]) for i in range(len(titles))]
        header = "\033[0;35m\033[7m{}\033[m".format("".join(parts))
        print(header)

    def printRow(self, row_data, widths, additional_characters=None, cursor_line=False):
        parts = [self.formatLongLine(row_data[i], widths[i]) for i in range(len(row_data))]
        if not cursor_line:
            line = "\033[m{}\033[m\033[0;33m\033[7m{}\033[m".format("".join(parts), str(additional_characters))
        else:
            line = "\033[0;33m\033[7m{}{}\033[m".format("".join(parts), str(additional_characters))
        print(line)

    def printBody(self, rows, widths, longtext):
        lines = self.formatLongText(longtext, widths[-1])
        for i in range(len(rows)):
            row_data = rows[i]
            additional_characters = lines[i] if i < len(lines) else "".join([" "]*widths[-1])
            self.printRow(row_data, widths, additional_characters, i==self.current_row)

    def formatLongText(self, text, width=50):
        lines = []
        pattern = "\a|\v|\r|\t|\n|\033"
        if isinstance(text, str):
            text = re.sub(pattern, "", text)
            l = len(text)
            i = math.floor(l / width)
            j = l - i * width
            for k in range(0, i):
                lines.append(text[k*width:(k+1)*width])
            if j > 0:
                lines.append(self.formatLongLine(text[i*width:], width))
        return lines

    def formatLongLine(self, line, desiredLength=50):
        pattern = "\a|\v|\r|\t|\n|\033"
        if isinstance(line, str):
            line = re.sub(pattern, "", line)
            if len(line) > desiredLength:
                return line[:desiredLength-3] + "..."
            else:
                return line + "".join([" "]*(desiredLength-len(line)))
        else:
            return "".join([" "]*desiredLength)

    def on_press(self, key):
        if key == keyboard.Key.esc:
            return False
        elif key == keyboard.Key.down:
            self.current_row+=1
            if self.current_row >= 30:
                self.current_row = 29
                self.current_min += 1
                if self.current_min + 30 >= len(self.data):
                    self.current_min = len(self.data) - 30
            self.clearScreen()
            self.print()
        elif key == keyboard.Key.up:
            self.current_row-=1
            if self.current_row < 0:
                self.current_row = 0
                self.current_min -= 1
                self.current_min = max(0, self.current_min)
            self.clearScreen()
            self.print()
        elif key == keyboard.Key.left:
            # update data
            self.update()
            self.clearScreen()
            self.current_min = 0
            self.current_row = 0
            self.print()
        return True

    def run(self):
        self.clearScreen()
        self.print()
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        listener.join()
