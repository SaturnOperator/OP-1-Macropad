# OP-1-Macropad
Use your OP-1 as a macropad using this python script.

# Installation 

At the core this program runs on Python3 and uses two libraries, [RtMidi](https://www.music.mcgill.ca/~gary/rtmidi/) to interfaces with midi IO and [Qt 5](https://doc.qt.io/qt-5/) which is a GUI framework.

```bash
pip install python-rtmidi
```

```bash
pip install PyQt5
```

The [PHue](https://github.com/studioimaginaire/phue) library is used for Philips Hue integration. This can be disabled if you delete the `PhilipsHueController` class and remove it's use in the `MainWindow` class initializer. (This will be simplified later on) 

Otherwise to install it use:

```bash
pip install phue
```

### Running

Simply run `main.py`

```bash
python3 main.py
```

# Using the Philips Hue features:

Press the green <u>drums button</u> to enter light controlling mode. 

The four encoders control the brightness of the four lights you set it up to. Clicking the encoder turns that light on/off.

Pressing numbers <u>1</u> through <u>4</u> under the screen will give you more control over the light you selected. 

 - The blue encoder controls brightness and turns the light on/off when clicked.
 - The green encoder controls the light's hue. Click on this makes the light purple.
 - The white encoder controls saturation. Clicking this resets the saturation.
 - The orange encoder controls colour temperature. Clicking this resets the light to the default warm white.