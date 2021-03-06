# Note that since qtile configs are just python scripts, you can check for
# syntax and runtime errors by just running this file as is from the command
# line, e.g.:
#
#    python config.py
import logging

from libqtile.manager import Key, Screen, Group, Drag, Click
from libqtile.command import lazy
from libqtile import layout, bar, widget, hook


# initialize logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
file_handler = logging.FileHandler('qtile.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
logger = logging.getLogger(__name__)

try:
    # bar font options
    font_options = {
        'font': 'Consolas',
        'fontsize': 16,
        'padding': 3,
    }

    # The screens variable contains information about what bars are drawn where on
    # each screen. If you have multiple screens, you'll need to construct multiple
    # Screen objects, each with whatever widgets you want.
    #
    # Below is a screen with a top bar that contains several basic qtile widgets.
    # global font options
    screens = [
        Screen(
            bottom=bar.Bar(
                [
                    widget.Spacer(width=200),

                    # This is a list of our virtual desktops.
                    widget.GroupBox(urgent_alert_method='text', **font_options),

                    widget.Spacer(width=50),
                    # A prompt for spawning processes or switching groups. This will be
                    # invisible most of the time.
                    widget.Prompt(),
                    # widget.Notify(),  # not available (why?)
                    widget.CurrentLayout(**font_options),
                    widget.Volume(**font_options),
                    widget.Battery(
                        energy_now_file='charge_now',
                        energy_full_file='charge_full',
                        power_now_file='current_now',
                        fontsize=14,
                        ),
                    widget.Systray(),
                    widget.Clock('%Y-%m-%d %a %I:%M %p', **font_options),
                    widget.WindowName(**font_options),
                    ],
                30)
            )
        ]

    # Super_L (the Windows key) is typically bound to mod4 by default, so we use
    # that here.
    mod = "mod4"

    # The keys variable contains a list of all of the keybindings that qtile will
    # look through each time there is a key pressed.
    keys = [
        # Admin commands
        Key([mod, "control"], "q",     lazy.shutdown()),
        Key([mod, "control"], "r",     lazy.restart()),
        Key([mod], "Return",           lazy.spawn("urxvt")),
        Key([mod], "F2", lazy.spawn("dmenu_run -fn 'Monospace:size=10' -nb '#000000' -nf '#fefefe'")),
        Key([mod], "F4", lazy.spawn("slock")),
        # Key([mod], "F4", lazy.spawn("gnome-screensaver-command -l")),
        Key([mod, "shift"], "c",       lazy.window.kill()),

        # Layout commands
        Key([mod], "k",                lazy.layout.down()),
        Key([mod], "j",                lazy.layout.up()),
        Key([mod], "h",                lazy.layout.previous()),
        Key([mod], "l",                lazy.layout.next()),
        Key([mod, "control"], "k",     lazy.layout.shuffle_up()),
        Key([mod, "control"], "j",     lazy.layout.shuffle_down()),
        # move_up() and move_down() are only supported by tree layout
        Key([mod, "shift"], "k",       lazy.layout.move_up()),
        Key([mod, "shift"], "j",       lazy.layout.move_down()),
        Key([mod, "shift"], "h",       lazy.layout.client_to_previous()),
        Key([mod, "shift"], "l",       lazy.layout.client_to_next()),
        Key([mod], "d",                lazy.layout.toggle_split()),
        Key([mod, "shift"], "space",   lazy.window.toggle_floating()),
        Key([mod], "F12",              lazy.window.toggle_fullscreen()),
        Key([mod], "u",                lazy.layout.rotate()),
        Key([mod], "Tab",              lazy.nextlayout()),
        # decrease_ratio() and increase_ratio() are only supported by tile layouts
        Key([mod], "q", lazy.layout.decrease_ratio()),
        Key([mod], "e", lazy.layout.increase_ratio()),

        # Change the volume if your keyboard has special volume keys.
        Key(
            [], "XF86AudioRaiseVolume",
            lazy.spawn("amixer -c 0 -q set Master 2dB+")
        ),
        Key(
            [], "XF86AudioLowerVolume",
            lazy.spawn("amixer -c 0 -q set Master 2dB-")
        ),
        Key(
            [], "XF86AudioMute",
            lazy.spawn("amixer -c 0 -q set Master toggle")
        ),

        # Also allow changing volume the old fashioned way.
        Key([mod], "equal", lazy.spawn("amixer -c 0 -q set Master 2dB+")),
        Key([mod], "minus", lazy.spawn("amixer -c 0 -q set Master 2dB-")),
    ]

    # This allows you to drag windows around with the mouse if you want.
    mouse = [
        Drag([mod], "Button1", lazy.window.set_position_floating(),
            start=lazy.window.get_position()),
        Drag([mod], "Button3", lazy.window.set_size_floating(),
            start=lazy.window.get_size()),
        Click([mod], "Button2", lazy.window.bring_to_front())
    ]

    # Border settings for layouts
    border = dict(
        border_normal='#808080',
        border_width=4,
    )

    # Two basic layouts.
    layouts = [
        # 30in monitor
        layout.Stack(stacks=[40, 40, 20], name='s404020', **border),
        layout.Stack(stacks=[60, 40], name='s6040', **border),
        layout.Stack(stacks=[80, 20], name='s8020', **border),
        layout.Max(),

        # # 23in monitor
        # layout.Stack(stacks=[50, 50], **border),
        # layout.Stack(stacks=[40, 60], **border),
        # layout.Max(),
    ]

    @hook.subscribe.client_new
    def idle_dialogues(window):
        if window.window.get_name() in (
            'NVIDIA X Server Settings',
            'Really quit?',
            'Disable Display Device',
            ):
        # # The below code causes crashes
        # window_name = window.window.get_name()
        # if window_name in (
        #         'NVIDIA X Server Settings',
        #         'Really quit?',
        #         'Disable Display Device',
        # ) or window_name.startswith(
        #     (
        #         'Opening ',
        #     )
        # ):
            window.floating = True

    # Specify group names, and use the group name list to generate an appropriate
    # set of bindings for group switching.
    groups = [
        Group('1-main', layout='s404020'),
        Group('2-email', layout='s6040'),
        Group('3-vm', layout='s8020'),
        Group('4-misc', layout='s8020'),
    ]
    for i, group in enumerate(groups, start=1):
        keys.append(
            Key([mod], str(i), lazy.group[group.name].toscreen())
        )
        keys.append(
            Key([mod, "shift"], str(i), lazy.window.togroup(group.name))
        )

except Exception:
    logger.exception('config failed')
