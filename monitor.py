import psutil, time, datetime
from inky import InkyPHAT
# init the inky display
inky_display = InkyPHAT("red")
inky_display.set_border(inky_display.RED)
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne
font = ImageFont.truetype(FredokaOne, 22)
print(""" The Inky system monitor """)


class System_stats():

    def __init__(self, interval=0.1, choice_menu=["cpu%", "mem%", "disk%", "uptime" ]):
        self.choice_menu = choice_menu
        self.interval = interval
        # initialize the disired statistics
        self.stats = {}
        self.iter_over_choice(self.psutil_choose)
        print("initialized the system statistics")

        
    def psutil_choose(self, choice):
        if choice == "cpu%":
            self.stats["cpu%"] =  psutil.cpu_percent(interval=None)
        elif choice == "mem%":
            self.stats["mem%"] = psutil.virtual_memory()[2]
        elif choice == "disk%":
            self.stats["disk%"] = psutil.disk_usage("/")[3]
        elif choice == "uptime":
            self.stats["uptime"] = str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).split(".")[0]
 

    def iter_over_choice(self, function):
        for choice in self.choice_menu:
            print(function(choice))
            
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
class Display():
    
    def __init__is(self):
        None
        
    def render(self, message):    
        img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
        draw = ImageDraw.Draw(img)
        draw.text((5, 5), str(dictToString(message)), inky_display.BLACK, font)
        inky_display.set_image(img)
        inky_display.show()


def main():
    statistics = System_stats(10)
    statistics.monitor()

if __name__ == "__main__":
    main()


