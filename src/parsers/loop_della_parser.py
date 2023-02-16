from .della_parser import DellParser
from time import sleep


class LoopDellParser(DellParser):

    def loop_parse(self):
        while True:
            self.parser_site()
            sleep(300)
