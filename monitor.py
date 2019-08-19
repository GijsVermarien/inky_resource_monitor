import psutil, time, datetime
from inky import InkyPHAT
# init the inky display
inky_display = InkyPHAT("red")
inky_display.set_border(inky_display.RED)
from PIL import Image, ImageFont, ImageDraw
print(""" The Inky system monitor """)


class System_stats():

    def __init__(self, interval=1, choice_menu=["cpu%", "mem%", "disk%", "uptime", "time" ]):
        self.choice_menu = choice_menu
        self.interval = interval
        # initialize the disired statistics
        self.stats = {}
        self.iter_over_choice(self.psutil_choose)
        print("initialized the system statistics")

        
    def psutil_choose(self, choice):
        """ choose a metric, retrieve it and then 
        pass it to the dict stats when called. """
        if choice == "cpu%":
            self.stats["cpu%"] =  str(psutil.cpu_percent(interval=None))
        elif choice == "mem%":
            self.stats["mem%"] = str(psutil.virtual_memory()[2])
        elif choice == "disk%":
            self.stats["disk%"] = str(psutil.disk_usage("/")[3])
        elif choice == "uptime":
            self.stats["uptime"] = str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).split(".")[0]
        elif choice == "time":
            self.stats["time"] = str(datetime.datetime.now().strftime("%H:%M %Y/%m/%d"))
        # ideas:
        # monitor higher core utilization
        # monitor gpu utilization with gpustat

    def iter_over_choice(self, function):
        """ Do not pass functions that require that
        something be returned 
        """
        for choice in self.choice_menu:
            function(choice)
            
    def update(self):
        self.iter_over_choice(self.psutil_choose)      
        return self.stats

    def monitor(self):
        i=1
        display = Display() 
        while i < 100:
            time.sleep(self.interval)
            self.update()
            display.render(self.stats)
            i += 1

def dictToString(dict):
      return str(dict).replace(', ','\r\n').replace("u'","").replace("'","")[1:-1]


class Sketch(object):
    """ Called sketch because draw was already taken, contains all the variables that can be drawn."""
    def __init__(self, draw, stats):
        self.draw = draw
        self.stats = stats
        self.white = inky_display.WHITE
        self.red = inky_display.RED
        self.black = inky_display.BLACK
        self.font = ImageFont.truetype("Inconsolata-Regular.ttf", 15)
        self.smallfont = ImageFont.truetype("Inconsolata-Regular.ttf", 10)
        self.display_metrics = [214, 104]

    def text_right_align(self, pos, text_element, color=None, font=None):
        """Automatically align text right based on coordinates of the top right corner"""
        text_w, text_h = self.draw.textsize(text_element, self.font)
        pos = tuple([pos[0] - text_w ,pos[1]]) 
        self.draw.text(pos, text_element, color, font)

    def text_center_align(self, pos_top_left, pos_bottom_right, text_element, color=None, font=None):
        """Align the text in the center based on the right top and left bottom corner """
        text_w, text_h = self.draw.textsize(text_element, self.font)
        x_pos = (pos_top_left[0] + pos_bottom_right[0] - text_w )/2
        y_pos = (pos_top_left[1] + pos_bottom_right[1] - text_h )/2
        pos = tuple([x_pos, y_pos])
        self.draw.text(pos, text_element, color, font)
    
    def draw_pie(self, pos_top_left, pos_bottom_right, percentage, color=None):
        start = -90
        end = -90 + float(percentage)*3.60
        self.draw.pieslice([pos_top_left, pos_bottom_right], start, end, color)
    
    def calculate_background_circle(self, tlc, rbc):
        """calculates the position of the background circle
        and also returns the size of the text frame"""
        text_w, text_h = self.draw.textsize("100.0", self.font)
        max_rad = ((text_w**2 + text_h**2)/4)**0.5
        circle_tlc = tuple([(tlc[0]+rbc[0])/2-max_rad, (tlc[1]+rbc[1])/2-max_rad])
        circle_rbc = tuple([(tlc[0]+rbc[0])/2+max_rad, (tlc[1]+rbc[1])/2+max_rad])
        return([circle_tlc, circle_rbc])

    def draw_background_circle(self, tlc, rbc, text):
        coords =  self.calculate_background_circle(tlc, rbc)
        self.draw.ellipse(coords, fill=self.white) 
        

    def draw_stat_name(self, tlc, rbc, name):
        assert len(name) <= 3    
        center_tex_w, center_text_h = self.draw.textsize("100.0", self.font)
        text_w, text_h = self.draw.textsize(name, self.smallfont)
        x_pos = (tlc[0]+rbc[0]-text_w)/2
        y_pos = (tlc[1]+rbc[1]-text_h-center_text_h-5)/2
        pos = [x_pos, y_pos]
        self.draw.text(pos, name, self.red, self.smallfont)


    def dynamic_circle(self, tlc, rbc, stats, name):
        self.draw.rectangle([tlc, rbc], outline=self.red)
        self.draw_pie(tlc, rbc, stats, self.black)
        self.draw_background_circle(tlc, rbc, stats)
        self.text_center_align(tlc, rbc, stats, self.black, self.font)
        self.draw_stat_name(tlc, rbc, name)

    def time(self):
        self.text_right_align((214, 0), self.stats["time"], self.black, self.font)
    
    def cpu(self):
        tlc = (0, 20) # Define top left corner
        rbc = (70, 90) # Define bottom right corner
        self.dynamic_circle(tlc, rbc, self.stats["cpu%"], "CPU")

    def mem(self):
        tlc = (72 , 20)
        rbc = (142, 90)
        self.dynamic_circle(tlc, rbc, self.stats["mem%"], "RAM")



class Display(object):
    """Initialize, create and send an image to the eink display """
    def __init__(self):
        pass
        
    def compose(self):
        """ choose what to add to the image """
        self.sketch = Sketch(self.draw, self.stats)
        self.sketch.time()
        self.sketch.cpu()
        self.sketch.mem()
        self.draw = self.sketch.draw

    def render(self, stats):
        """ create a new image, draw things on it in compose and then send it to eink display"""
        self.stats = stats
        self.img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
        self.draw = ImageDraw.Draw(self.img)
        self.compose()
        inky_display.set_image(self.img)
        inky_display.show()


    
def main():
    statistics = System_stats(10)
    statistics.monitor()

if __name__ == "__main__":
    main()


