
class AnimalRace():
    spriteCount=7
    sprites={"cheese":[[u'// The cheese is already done (it has hidden scripts).'],1],
    "Horse":[[u'when this sprite clicked // This makes the horse race when you click it\nglide to finish line',
    u'when @greenFlag clicked // This script initializes (resets) the horse when you click on the green flag.  Write a script like this for the cat and rooster to help them!\ngo to x:246 y:71'],1],
    "fish":[[u'// The fish is already done (it has hidden scripts).'],1],
    "Rooster":[[u'when this sprite clicked // This makes the rooster race when you click it.\nfast glide 150 steps\npoint in direction up\nmedium glide 50 steps\nturn @turnRight 30 degrees\nslow glide 20 steps\nturn @turnLeft 90 degrees\nfast glide 100 steps\nturn @turnRight 30 degrees\nmedium glide 50 steps\npoint in direction left\nfast glide 150 steps\npoint in direction right',
    u'// write a script to initialize (reset) the rooster!'],1],
    "Cat":[[u'when this sprite clicked // This makes the cat race when you click it.\nglide to cheese\nchange size by 10\nglide to fish\nchange size by 10\nglide to mouse\nchange size by 10\nslow glide 50 steps',
    u'// Write a script to initialize (reset) the cat!'],1],
    "mouse":[[u'// The mouse is already done (it has hidden scripts).'],1],
    "finish line":[[u'// The finish line is already done (it has hidden scripts).'],1]}
    addOkay=True
class CAGeography():
    spriteCount=6
    sprites={"LakeTaho":[[],1],
    "SanFrancisco":[[],1],
    "Fresno":[[],1],
    "Sacramento":[[u'// This sprite has a hidden script. Try clicking on the sprite!'],1],
    "SantaBarbara":[[],1],
    "LosAngeles":[[],1]}
    addOkay=True
class CAGeographyBroadcast():
    spriteCount=7
    sprites={"LosAngeles":[[],1],
    "SanFrancisco":[[],1],
    "Fresno":[[],1],
    "Sacramento":[[],1],
    "LakeTahoe":[[],1],
    "SantaBarbara":[[u"when this sprite clicked\nbroadcast 'Santa Barbara'"],1],
    "Car":[[u"when I receive 'Santa Barbara'\nsay 'Santa Barbara' for 2 secs\ngo to SantaBarbara",
    'when @greenFlag clicked\ngo to x:141 y:-48'],1]}
    addOkay=True
class DanceParty():
    spriteCount=3
    sprites={"Ballerina":[[u'when this sprite clicked\nswitch costume to squat\nwait 0.5 secs\nswitch costume to stand\nwait 0.5 secs\nswitch costume to jump\npoint in direction 90\nglide 50 steps\nwait 0.5 secs\nswitch costume to twirl\nwait 0.2 secs\nswitch costume to twirlback\nwait 0.2 secs\nswitch costume to twirl\nwait 0.2 secs\nswitch costume to twirlback\nwait 0.2 secs\nswitch costume to twirl\nwait 0.2 secs\nswitch costume to squat\nwait 0.3 secs\nswitch costume to jump\npoint in direction -90\nmove 50 steps\nwait 0.5 secs\nswitch costume to stand',
    u'when @greenFlag clicked\nset size to 70%\ngo to x:-120 y:-83\nswitch costume to stand\npoint in direction 90'],5],
    "Cassy":[['when @greenFlag clicked\nswitch costume to cassy-chillin\nset size to 80%\ngo to x:166 y:77'],8],
    "CoolDude":[['when @greenFlag clicked\nset size to 80%\ngo to x:-138 y:79\nswitch costume to breakdancer-1',
    u'when this sprite clicked\nswitch costume to breakdancer-3\nswitch costume to breakdancer-4\nswitch costume to breakdancer-2\nswitch costume to breakdancer-3\nswitch costume to breakdancer-1'],4]}
    addOkay=True
class EgyptGame():
    spriteCount=6
    sprites={"Hero":[[u"when I receive 'Level0'\npen down\nglide 350 steps\nturn @turnLeft 90 degrees\nglide 150 steps\npen up",
    u"when I receive 'Level1'",
    u"when I receive 'Level2'",
    u"when I receive 'Level3'"],3],
    "Target":[[u"when @greenFlag clicked\nset size to 30%\nswitch costume to Finish Costume\ngo to x:175 y:6\nset localReset to (1 - (Reset))\nforever\n    if ((Reset) = (localReset)) then\n        set Points to (BasePoints)\n        switch costume to Finish Costume\n        wait until ((heroMoving) = '0')\n        switch costume to Finish Costume\n        set Reset to (1 - (Reset))\n        broadcast 'ResetHero' and wait\n        broadcast 'Reset'\n    end\n    if (touching Hero?) then\n        set BasePoints to (Points)\n        change Level by 1\n        repeat 5\n            change color effect by 25\n        end\n        set color effect to 0\n        wait until ((heroMoving) = '0')\n        set Reset to (1 - (Reset))\n        broadcast 'ResetHero' and wait\n        broadcast 'Reset'\n    end\nend"],4],
    "Dog":[['when @greenFlag clicked\nset size to 40%\ngo to x:-134 y:-27',
    u"when I receive 'Reset'\nset localReset to (1 - (Reset))\nif ((Level) = '0') then\n    hide\nend\nif ((Level) = '3') then\n    go to x:-129 y:-15\n    show\nend\nrepeat until ((Reset) = (localReset))\n    if (touching Hero?) then\n        repeat 5\n            change color effect by 25\n        end\n        set color effect to 0\n        set Reset to (1 - (Reset))\n        wait until ((heroMoving) = '0')\n        broadcast 'ResetHero' and wait\n        broadcast 'Reset'\n    end\nend"],2],
    "Lake":[['when @greenFlag clicked\nset size to 70%\ngo to x:32 y:-21',
    u"when I receive 'Reset'\nset localReset to (1 - (Reset))\nif ((Level) = '0') then\n    go to x:44 y:-14\n    hide\nend\nif ((Level) = '1') then\n    go to x:100 y:0\n    hide\nend\nif ((Level) = '2') then\n    hide\nend\nif ((Level) = '3') then\n    go to x:67 y:-17\n    show\nend\nrepeat until ((Reset) = (localReset))\n    if (touching Hero?) then\n        repeat 5\n            change color effect by 25\n        end\n        set color effect to 0\n        set Reset to (localReset)\n        wait until ((heroMoving) = '0')\n        broadcast 'ResetHero' and wait\n        broadcast 'Reset'\n    end\nend"],2],
    "Rock":[['when @greenFlag clicked\nhide\nset size to 70%',
    u"when I receive 'Reset'\nset localReset to (1 - (Reset))\nif ((Level) = '0') then\n    hide\nend\nif ((Level) = '1') then\n    go to x:-75 y:-140\n    hide\nend\nif ((Level) = '2') then\n    go to x:-95 y:-120\n    show\nend\nif ((Level) = '3') then\n    go to x:-105 y:-140\n    show\nend\nrepeat until ((Reset) = (localReset))\n    if (touching Hero?) then\n        repeat 5\n            change color effect by 25\n        end\n        set color effect to 0\n        set Reset to (1 - (Reset))\n        wait until ((heroMoving) = '0')\n        broadcast 'ResetHero' and wait\n        broadcast 'Reset'\n    end\nend"],2],
    "Fish1":[['when @greenFlag clicked\nset size to 50%',
    u"when I receive 'Reset'\nset localReset to (1 - (Reset))\nif ((Level) = '1') then\n    go to x:-51 y:47\n    show\nend\nif ((Level) = '0') then\n    go to x:-51 y:47\n    hide\nend\nif ((Level) = '2') then\n    go to x:-51 y:47\n    show\nend\nif ((Level) = '3') then\n    go to x:-51 y:47\n    show\nend\nrepeat until ((Reset) = (localReset))\n    if (touching Hero?) then\n        change Points by 1\n        hide\n    end\nend"],2]}
    addOkay=True
class GoldRush():
    spriteCount=5
    sprites={"Gold Finder":[['next costume\nwait 0.2 secs\nmove 10 steps\nnext costume\nwait 0.2 secs\nmove 10 steps',
    u'// This is how you can make me walk!'],4],
    "Button":[['when @greenFlag clicked\nshow',
    u"when this sprite clicked\nbroadcast 'Scene1'\nhide"],1],
    "Gold Pan":[[],3],
    "PurpleArrow":[[],1],
    "BlueArrow":[[],1]}
    addOkay=True
class IntroGame():
    spriteCount=23
    sprites={"Block15":[[],5],
    "Block14":[[],5],
    "Block13":[[],5],
    "Block12":[[],5],
    "Block11":[[],5],
    "Block10":[[],5],
    "Dog":[[],1],
    "Baby":[[],1],
    "Up":[[],1],
    "Cat":[[],1],
    "Block4":[[],5],
    "Left":[[],1],
    "Block7":[[],5],
    "Block6":[[],5],
    "Block5":[[],5],
    "Right":[[],1],
    "Block3":[[],5],
    "Block2":[[],5],
    "Block1":[[],5],
    "Move":[[],1],
    "Block9":[[],5],
    "Block8":[[],5],
    "Down":[[],1]}
    addOkay=True
class MammalsGame():
    spriteCount=20
    sprites={"Horse":[[],1],
    "Sprite15":[[],1],
    "Sprite9":[[],1],
    "Bear":[[],1],
    "Sprite10":[[],1],
    "Sprite11":[[],1],
    "Sprite12":[[],1],
    "Sprite13":[[],1],
    "Sprite14":[[],1],
    "Snake":[[],1],
    "Sprite8":[[],1],
    "Zebra":[[],1],
    "Sprite6":[[],1],
    "Sprite7":[[],1],
    "Net":[['when this sprite clicked\npoint in direction 90\nglide 50 steps\npoint in direction 180\nglide 50 steps\nglide 50 steps\nglide 50 steps'],1],
    "Sprite5":[[],1],
    "Sprite2":[[],1],
    "Sprite3":[[],1],
    "Sprite4":[[],1],
    "Sprite1":[[],1]}
    addOkay=True
class Missions():
    spriteCount=6
    sprites={"Sprite 3":[[],2],
    "Sprite 2":[[u'// This script has been implemented so you can see how it works, but the script is hidden from you so you do not see what blocks to use.'],2],
    "Sprite 1":[[],2],
    "Sprite 5":[[],2],
    "Sprite 4":[[],2],
    "Missionary":[[],1]}
    addOkay=True
class MissionsBroadcast():
    spriteCount=6
    sprites={"San Juan Batista":[[],2],
    "Sacramento":[[],2],
    "San Diego":[[],2],
    "San Francisco":[[],2],
    "Santa Barbara":[[u'// This sprite has a hidden script'],2],
    "Missionary":[[u'// This sprite has a hidden script'],1]}
    addOkay=True
class Planets():
    spriteCount=10
    sprites={"Mercury":[[],1],
    "Rocket":[[u'when up arrow key pressed // The rocket already goes up correctly when the up arow key is pressed. Add the code to make the rest of the arrows navigate the rocket correctly.\n                          // \npoint in direction 0\nmove 10 steps'],1],
    "Sun":[[u'// The code for the sun has already been implemented. It is hidden from you.'],1],
    "Neptune":[[],1],
    "Jupiter":[[],1],
    "Uranus":[[],1],
    "Mars":[[],1],
    "Earth":[[],1],
    "Venus":[[],1],
    "Saturn":[[],1]}
    addOkay=True
class PlanetsBroadcast():
    spriteCount=10
    sprites={"Mercury":[[],1],
    "Sun":[[u'// Notice what happens when you click on the sun.  The code has been implemented, but it is hidden from you.'],1],
    "Neptune":[[],1],
    "Sprite10":[[u"// The code has already been implemented for the sun.  Watch what it does and try to do somethign similar for the rest of the planets.  Also, don't forget to initialize!!!"],1],
    "Jupiter":[[],1],
    "Uranus":[[],1],
    "Mars":[[],1],
    "Earth":[[],1],
    "Venus":[[],1],
    "Saturn":[[],1]}
    addOkay=True
class PlantGrowing():
    spriteCount=3
    sprites={"Sun":[['when @greenFlag clicked',
    u'// Remember to initialize!',
    u'// Which costume does it start on?',
    'when this sprite clicked',
    u'switch costume to ClickMeCostume',
    u'// What should happen when it is clicked?',
    u'switch costume to Rays',
    'hide',
    u'// When should it appear?  When should it disappear?',
    'show'],2],
    "Button":[['when @greenFlag clicked',
    u'// Remember to initialize!',
    'show',
    u'// When should it appear?\n// When should it disappear?',
    'hide',
    'when this sprite clicked',
    u'// What should happen when it is clicked?'],1],
    "Cloud":[['when this sprite clicked',
    u'when @greenFlag clicked\npoint in direction 90\ngo to x:-10 y:55\nswitch costume to Not raining\nshow',
    u'// What should happen when it is clicked?',
    'hide',
    u'switch costume to Raining',
    u'// When should it disappear?',
    u'// When should it switch to the raining costume?'],2]}
    addOkay=True
class RaceGame():
    spriteCount=3
    sprites={"Horse":[['when a key pressed\npoint in direction -90'],1],
    "Sprite2":[[],1],
    "Bat":[['when @greenFlag clicked\npoint in direction 90\ngo to x:-188 y:-126'],1]}
    addOkay=True
class ThanksgivingGame():
    spriteCount=10
    sprites={"Bridge":[[],1],
    "Target":[[],2],
    "Native Americans":[[],1],
    "Corn":[[],1],
    "Bear":[[],2],
    "Pilgrims":[[u"when I receive 'Level3'",
    u"when I receive 'Level0'\npen down\nturn @turnLeft 90 degrees\nglide 170 steps\nturn @turnRight 90 degrees\nglide 400 steps\npen up",
    u"when I receive 'Level1'",
    u"when I receive 'Level4'",
    u"when I receive 'Level2'",
    u"when I receive 'Level5'"],1],
    "Cornstalks":[[],1],
    "Trap":[[],3],
    "River":[[],1],
    "Fish":[[],1]}
    addOkay=True