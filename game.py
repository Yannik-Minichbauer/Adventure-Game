#from adventurelib import *
import adventurelib_yannik as a
import random
import PySimpleGUI as sg
a.Room.items = a.Bag()

# each room shall have a image-filename attribute

#TODO:(zoombare) room-rmap entweder als: Frames, Buttons?, Graph-Element, table?
#TODO: talk to (self) behauptet fälschlich es ist niemand da

current_room = starting_room = a.Room("""
You are in a dark room.
""", image="room.png")


valley = starting_room.north = a.Room("""
You are in a beautiful valley.
""", image="valley.png")

magic_forest = valley.north = a.Room("""
You are in a enchanted forest where magic grows wildly.
""", image="forest.png")

cave = magic_forest.west = a.Room("""
You are inside a dark cave.
You hear a waterfall nearby""", image="cave.png")


mallet = a.Item('rusty mallet', 'mallet')
valley.items = a.Bag({mallet,})

wizard = a.Item('wizard', 'the wizard', 'a wizard')
wizard.answers = ["Geht so", "jaja", "akra-ka-babra!"]

# a bag is a python SET !!
magic_forest.items = a.Bag({wizard,}) # ITEMS must be in a bag

inventory = a.Bag()

@a.when('go north', direction="north")
@a.when("go south", direction="south")
@a.when("go east", direction="east")
@a.when("go west", direction="west")
#@a.when('north', direction='north')
#@a.when('south', direction='south')
#@a.when('east', direction='east')
#@a.when('west', direction='west')
def go(direction):
    global current_room
    room = current_room.exit(direction)
    if room:
        current_room = room
        a.say('You go %s.' % direction)
        look()
        if room == magic_forest:
            a.set_context('magic_aura')
        else:
            a.set_context('default')


@a.when('take ITEM')
def take(item):
    if item == "wizard":
        a.say("The wizard does not want to be picked up by you")
        return
    obj = current_room.items.take(item)
    if obj:
        a.say('You pick up the %s.' % obj)
        inventory.add(obj)
    else:
        a.say('There is no %s here.' % item)


@a.when("talk THING")
@a.when("talk to THING")
def talk(thing):
    if thing == "to" or thing == None:
        a.say("You talk a bit to yourself")
        return
    # check if the thing is in the inventory or in the current room
    # inventory and room.items are SET's. to merge them, I use pythons join command
    for i in inventory.union(current_room.items):
        if thing in i.aliases:
            exist = True
            break
    else:
        # else in a for loop means the whole loop was interrated trough, without any break
        a.say("there is no {} to talk to, neither in your inventory nor in this room/location".format(thing))
        return
    # the thing exist. thing is a string, i is the object
    a.say("you talk to {}...".format(thing))
    # check if object i (the item) has the .answers attribute
    if "answers" in i.__dict__.keys():
        a.say("and the {} says: '{}'".format(thing, random.choice(i.answers)))
    else:
        a.say("but you get no reply. None at all. It seems that the {} is unable to talk".format(thing))





@a.when('drop THING')
def drop(thing):
    obj = inventory.take(thing)
    if not obj:
        a.say('You do not have a %s.' % thing)
    else:
        a.say('You drop the %s.' % obj)
        current_room.items.add(obj)


@a.when('look')
def look():
    a.say(current_room)
    #a.say("image: {}".format(current_room.image))
    if current_room.items:
        for i in current_room.items:
            a.say('A %s is here.' % i)


@a.when('inventory')
def show_inventory():
    a.say('You have:')
    for thing in inventory:
        a.say(thing)

@a.when('cast', magic=None, context='magic_aura')
@a.when("cast MAGIC", context='magic_aura')
def cast(magic):
    if magic == None:
        a.say("Which magic you would like to spell?")
    elif magic == "fireball":
        a.say("you cast a flaming Fireball! Woooosh....")


# ---- new functons for gui ---



def command_list():
    return [c for c in commands]

def inventory_list():
    return [i for i in inventory]

def item_list():
    return [i for i in current_room.items]


@a.when("help")
def printhelp():
    li = a.helplist()
    for c in li:
        print(c)

# ------------------ GUI ------------------

##[sg.Text("", size=(15, 1)), sg.Button("North", size=(10, 1)), sg.Text("", size=(15, 1))],
##[sg.Button("West", size=(10, 1)), sg.Text("", size=(15, 1)), sg.Button("East", size=(10, 1))],
##[sg.Text("", size=(15, 1)), sg.Button("South", size=(10, 1)), sg.Text("", size=(15, 1))],
##[sg.Text("image file name:"), sg.Text("", key="image", size=(15,1))],
sidescreen = [
               [sg.Frame(title="image:", layout=[[sg.Image(filename="room.png", key="image")]])],
               [sg.Text("valid commands", size=(17,1)), sg.Text("things here:", size=(17,1)), sg.Text("your inventory:", size=(17,1))],
               [sg.Listbox(key="help", size=(15,15), values=[], enable_events=True),
                sg.Listbox(key="things_here", values=[], size=(15,15), enable_events=True),
                sg.Listbox(key="inventory", values=[], size=(15,15),enable_events=True)
               ] ,
             ]

layout = [
          [sg.Text("Adventure - press start to begin", key="header",)],
          [sg.Output(key="output", visible=True, size=(70,2)),sg.Col(key="gui", layout=sidescreen, visible=False)],
          [sg.Col(key="inputline", visible=False, layout=[
             [sg.InputText(key="command", size=(50, 1), do_not_clear=False),
              sg.Button("execute", bind_return_key=True, size=(10,1))]])],
          [sg.Button("Start"), sg.Button("Cancel"), sg.Button("test")],
         ]

window = sg.Window(title="Adventuregame", layout=layout)

while True:
    event, values = window.read()
    if event in [None, "Cancel"]:
        break
    if event == "Start":
        window["header"].update("Game is running")
        a.say("starting a new adventure")
        #a.start()
        look()
        #window["output"].update(size=(70,15))
        window["gui"].update(visible=True)
        #window["command"].update(visible=True)
        #window["execute"].update(visible=True)
        window["inputline"].update(visible=True)
        window["Start"].update(visible=False)
    if event == "execute":
        a.say(">>> "+ values["command"].strip())
        a._handle_command(values["command"].strip())
    if event == "test":
        ugly = a._available_commands()
        print(ugly)
        #for t in ugly:
        #    print(t[0]])
        a.help()
    if event == "inventory":
        t = values["inventory"]
        if len(t) == 0:
            pass
        else:
            t = "drop " + str(t[0])
            window["command"].update(t)
            window.finalize()
            a.say(">>> " + t.strip())
            a._handle_command(t.strip())


    if event == "things_here":
        t = values["things_here"]
        if len(t) == 0:
            pass
        else:
            t = "take " + str(t[0])
            window["command"].update(t)
            window.finalize()
            a.say(">>> " + t.strip())
            a._handle_command(t.strip())
    if event == "help":
        #print("help wurde geklickt")
        #print(values["help"][0])
        c=values["help"][0]
        if "drop" in c:
            sg.popup_no_buttons("To drop an item click on the item in the 'Your inventory' list", no_titlebar=True, font=("Arial", 22, "normal"), auto_close=True,auto_close_duration=3)
        elif "take" in c:
            sg.popup_no_buttons("To take an item click on the item in the 'Things here' list", no_titlebar=True, font=("Arial", 22, "normal"), auto_close=True,auto_close_duration=3)
        elif "talk" in c:
            sg.popup("You must specify to whom you want to talk\nPlease write the command like: 'talk to Wizard'")
        elif "cast" in c:
            sg.popup("You must cast a specific spell\nplease write the command like: 'Cast Fireball'",no_titlebar=True, font=("Arial", 22, "normal"))
        else:
            window["command"].update(c)
            window.finalize()
            a.say(">>> " + c.strip())
            a._handle_command(c.strip())
    # update command and help list
    window["help"].update(a.helplist())
    window["inventory"].update(inventory_list())
    window["things_here"].update(item_list())
    # update image
    window["image"].update(current_room.image)
    
window.close()
print("bye")

# --------- adventure start ------

