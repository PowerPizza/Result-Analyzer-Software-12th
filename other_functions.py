class Add_Scroll:
    element_ = None
    root_window = None
    respect_to = None
    scroll_speed = 15
    scrolled_x = 2
    scrolled_y = 2
    _scroller_id = None
    def __init__(self, rt_, element, root_window):
        """
        :param rt_: respect to (rt_) means element should scroll with respect to which element like if a 600px square
        contains 900px square so if you want to scroll 900px square within 600px square so provide 600px square
        element in this parameter, by default provide root.
        :param element: the main element on which you want to add scroll on.
        :param root_window: application window or the element which help to emulate keypress for scroll it can be
        entry type or any focusable widget. by default provide Tk() object.
        """
        self.element_ = element
        self.root_window = root_window
        self.respect_to = rt_
        self.element_.update()
        self.root_window.update()

    def _scrollX_begin(self, eve):
        if eve.keycode == 39 and self.scrolled_x < 0:
            self.scrolled_x += self.scroll_speed
            self.element_.place(x=self.scrolled_x, y=self.scrolled_y)
        elif eve.keycode == 37 and self.scrolled_x > self.respect_to.winfo_width() - self.element_.winfo_width():
            self.scrolled_x -= self.scroll_speed
            self.element_.place(x=self.scrolled_x, y=self.scrolled_y)

    def  _scrollY_begin(self, eve):
        if eve.keycode == 38 and self.scrolled_y < 0:
            self.scrolled_y += self.scroll_speed
            self.element_.place(x=self.scrolled_x, y=self.scrolled_y)
        elif eve.keycode == 40 and self.scrolled_y > self.respect_to.winfo_height() - self.element_.winfo_height():
            self.scrolled_y -= self.scroll_speed
            self.element_.place(x=self.scrolled_x, y=self.scrolled_y)

    def start_scroll(self, dir_):
        """
        :param dir_: X , XY , Y represent scroll enabled directions
        """
        def scroll_parser(eve):
            if dir_ == "X":
                self._scrollX_begin(eve)
            elif dir_ == "Y":
                self._scrollY_begin(eve)
            elif dir_ == "XY":
                self._scrollX_begin(eve)
                self._scrollY_begin(eve)

        self._scroller_id = self.root_window.bind("<KeyPress>", scroll_parser)

    def stop_scroll_all(self):
        self.root_window.unbind("<KeyPress>", self._scroller_id)


def list_formatter(lst):
    """ removes '' or len 0 itm from list """
    for itm in lst:
        if len(itm) == 0:
            lst.remove(itm)
    return lst

if __name__ == '__main__':
    print(list_formatter(["hi", '', "ss", '']))
    pass