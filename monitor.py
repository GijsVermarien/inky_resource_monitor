from PIL import Image, ImageFont, ImageDraw
import argparse
import psutil
import time
import datetime
import os
import json
import argparse
import logging
import subprocess
try: 
    import gpustat
    can_gpu = True
    logging.info("Imported the gpustat package succesfully")
except: 
    can_gpu= False
    logging.info("Could not retrieve the gpustat package, now we cannot get gpu stats")
# init the inky display
try: 
    from inky.auto import auto
    from PIL import Image, ImageFont, ImageDraw
    inky_display = auto(ask_user=True, verbose=True)
    inky_display.set_border(inky_display.WHITE)
except:
    logging.info("Could not load inky display")
print(""" The Inky system monitor """)


class System_stats(object):
    """ The system that retrieves the statistics and writes them to self.stats"""

    def __init__(self, interval=1, choice_menu=["cpu%", "mem%", "disk%", "uptime", "time", "hostname", "gpu%"]):
        self.choice_menu = choice_menu
        self.interval = interval
        # initialize the disired statistics
        self.stats = {}
        self.iter_over_choice(self.psutil_choose)
        logging.info("Initialized the system statistics monitor")

    def psutil_choose(self, choice):
        """ choose a metric, retrieve it and then 
        pass it to the dict stats when called. """
        if choice == "cpu%":
            self.stats["cpu%"] = str(psutil.cpu_percent(interval=None))
        elif choice == "mem%":
            self.stats["mem%"] = str(psutil.virtual_memory()[2])
        elif choice == "disk%":
            self.stats["disk%"] = str(psutil.disk_usage("/")[3])
        elif choice == "uptime":
            self.stats["uptime"] = str(datetime.datetime.now(
            ) - datetime.datetime.fromtimestamp(psutil.boot_time())).split(".")[0]
        elif choice == "time":
            self.stats["time"] = str(
                datetime.datetime.now().strftime("%H:%M %m/%d"))
        elif choice == "hostname":
            self.stats["hostname"] = str(os.uname()[1])
        elif choice == "gpu%" and can_gpu:
            try: 
                self.stats["gpu%"] = str(gpustat.new_query()[0].utilization)
            except :
                logging.info("Failed to retrieve gpu statistics")
                self.stats["gpu%"] = "NaN"
        # ideas:
        # monitor higher core utilization

    def iter_over_choice(self, function):
        """ Do not pass functions that require that
        something be returned 
        """
        for choice in self.choice_menu:
            function(choice)

    def update(self):
        """ Update all the chosen stats and return the new ones """
        self.iter_over_choice(self.psutil_choose)
        return self.stats

    def watch_and_display_stats(self):
        """ Simple script to monitor on the Raspberry pi itself locally """
        display = Display()
        while True: 
            time.sleep(self.interval)
            self.update()
            display.render(self.stats)


class Host_daemon(System_stats):
    """Extension of System_stats in order to run as solely a host."""

    def __init__(self, interval, ssh_adress, rpi_path = "/home/pi/inky_resource_monitor"):
        super().__init__(interval)
        self.path = rpi_path
        self.adress = ssh_adress

    def watch_stats(self):
        failed_transfers = 0
        while True:
            begin = datetime.datetime.now()
            try:
                self.update()
            except:
                print("Could not update values")
            try:
                with open("stats.json", "w") as outfile:
                    json.dump(self.stats, outfile)
                scp_to_rpi = "scp ./stats.json {adress}:{path}".format(adress=self.adress, path=self.path)
                subprocess.call(scp_to_rpi, shell=True)
                failed_transfers = 0
            except:
                print("Could not transfer data")
                failed_transfers += 1
                if failed_transfers > 10:
                    break
            end = datetime.datetime.now()
            pausetime = self.interval - (end-begin).total_seconds()
            pausetime = (pausetime > 0)*pausetime
            time.sleep(pausetime)


class Display_daemon(System_stats):
    """ Extension of System_stats in order to display the statistics
    of another system"""

    def __init__(self, interval):
        super().__init__(interval)
        self._cached_stamp = 0
        self.filename = "./stats.json"

    def check_file(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp > self._cached_stamp:
            self._cached_stamp = stamp
            return True
        else:
            return False

    def display_remote_stats(self, gpu_switch):
        if gpu_switch:
            display = Gpu_display()
        else:
            display = Display()
        while True:
            if self.check_file():
                with open(self.filename, "r") as infile:
                    self.stats = json.load(infile)
                display.render(self.stats)
            else:
                time.sleep(0.1)


class Sketch(object):
    """ Called sketch because draw was already taken, does the actual drawing."""

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
        pos = tuple([pos[0] - text_w, pos[1]])
        self.draw.text(pos, text_element, color, font)

    def text_center_align(self, pos_top_left, pos_bottom_right, text_element, color=None, font=None):
        """Align the text in the center based on the right top and left bottom corner """
        text_w, text_h = self.draw.textsize(text_element, self.font)
        x_pos = (pos_top_left[0] + pos_bottom_right[0] - text_w)/2
        y_pos = (pos_top_left[1] + pos_bottom_right[1] - text_h)/2
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
        circle_tlc = tuple(
            [(tlc[0]+rbc[0])/2-max_rad, (tlc[1]+rbc[1])/2-max_rad])
        circle_rbc = tuple(
            [(tlc[0]+rbc[0])/2+max_rad, (tlc[1]+rbc[1])/2+max_rad])
        return([circle_tlc, circle_rbc])

    def draw_background_circle(self, tlc, rbc, text):
        coords = self.calculate_background_circle(tlc, rbc)
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
        self.text_right_align(
            (214, 0), self.stats["time"], self.black, self.font)

    def cpu(self, tlc=(0, 20), rbc=(70, 90)):
        self.dynamic_circle(tlc, rbc, self.stats["cpu%"], "CPU")

    def mem(self, tlc=(71, 20), rbc=(141, 90)):
        self.dynamic_circle(tlc, rbc, self.stats["mem%"], "RAM")

    def gpu(self, tlc=(142, 20), rbc=(214, 90)):
        self.dynamic_circle(tlc, rbc, self.stats["gpu%"], "GPU")

    def hostname(self):
        tlc = (0, 0)
        self.draw.text(
            (0, 0), self.stats["hostname"], self.black, self.font)

    def uptime(self):
        self.text_right_align((214, 89), "up: {i}".format(
            i=self.stats["uptime"]), self.black, self.font)
    

class Display(object):
    """Initialize, create and send an image to the eink display """

    def __init__(self):
        pass

    def compose(self):
        """ choose what to add to the image """
        self.sketch = Sketch(self.draw, self.stats)
        self.sketch.time()
        self.sketch.hostname()
        self.sketch.cpu(tlc=(35, 20), rbc=(105, 90))
        self.sketch.mem(tlc=(104, 20), rbc=(179, 90))
        self.sketch.uptime()
        self.draw = self.sketch.draw

    def render(self, stats):
        """ create a new image, draw things on it in compose and then send it to eink display"""
        self.stats = stats
        self.img = Image.new("P", (inky_display.WIDTH, inky_display.HEIGHT))
        self.draw = ImageDraw.Draw(self.img)
        self.compose()
        inky_display.set_image(self.img)
        inky_display.show()

class Gpu_display(Display):
    def __init__(self):
        pass

    def compose(self):
        """ choose what to add to the image """
        self.sketch = Sketch(self.draw, self.stats)
        self.sketch.time()
        self.sketch.hostname()
        self.sketch.cpu()
        self.sketch.mem()
        self.sketch.gpu()
        self.sketch.uptime()
        self.draw = self.sketch.draw

## Source: stackoverflow
def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", "-m", type=str, required=True, choices=[
                        "local", "server", "display"], help="choose the mode of operation")
    parser.add_argument("--ssh_adress", "-s", type=str, required=False,
            help="the username and ip adress for the display i.e. pi@192.168.0.7",
            default="0.0.0.0")
    parser.add_argument("--path", "-p", type=str, required = False, 
            help="the path of inky_resource_monitor on the rasperry pi",
            default="/home/pi/inky_resource_monitor/")
    parser.add_argument("--refreshrate", "-r", type=int, required=False,
                        help="at which rate must the program refresh",
                        default=30)
    parser.add_argument("--gpu", "-g", type=str2bool, required=False, 
	    help="do you want to monitor you nvidia gpu?", default=False)
    # idea: add an option that allows for choosing what to watch, as defined in the System_stats
    args = parser.parse_args()
    
    if args.mode == "display":
        daemon = Display_daemon(None)
        daemon.display_remote_stats(args.gpu)
    elif args.mode == "server":
        daemon = Host_daemon(args.refreshrate, args.ssh_adress, args.path)
        daemon.watch_stats()
    else: 
        daemon = System_stats(args.refreshrate)
        daemon.watch_and_display_stats()
    print("shutting the service down")


if __name__ == "__main__":
    main()
