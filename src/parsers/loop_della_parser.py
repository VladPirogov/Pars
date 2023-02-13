from .della_parser import DellParser
from time import sleep


class LoopDellParser(DellParser):

    def loop_parse(self):
        while True:
            sleep(300)
            self.parser_site()