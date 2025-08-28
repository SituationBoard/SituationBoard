# Manual Installation
To install SituationBoard you can use the automatic setup functionality provided by the ```sbctl``` tool (as described in [README.md](../README.md)).
In addition, you can also install SituationBoard manually. Below is a description of the manual installation process.
It assumes you are using Raspbian (aka Raspberry Pi OS) or another Debian-based Linux distro.
The installation is divided into a general part (base installation) and optional parts
that are only required when specific features are actually needed:

| Feature       | Description                                                                                 | Hardware Requirements  |
|---------------|---------------------------------------------------------------------------------------------|------------------------|
| **GPIO**      | Required to receive alarms via binary inputs and to toggle outputs in reaction to an alarm  | Raspberry Pi           |
| **SMS**       | Required to receive alarms via SMS                                                          | Cellular modem         |
| **AUTOSTART** | Required for production use (takes care of frontend autostart and other system adjustments) | -                      |
| **TEST**      | Required to run automatic tests (used for development)                                      | -                      |

## General Setup

### Enable SSH and autologin for the desired user
To allow for remote access to the device you can enable the SSH daemon.
Additionally, you should make sure that GUI autologin is enabled for the desired user.
This allows to show SituationBoard automatically after a reboot.
To enable both options on Raspbian use the tool ```raspi-config```:
```
sudo raspi-config
```

### Download SituationBoard
Open a terminal, clone this GIT repository to the target machine and switch to the downloaded folder:
```
git clone git@github.com:SituationBoard/SituationBoard.git
cd SituationBoard
```

### Install essential tools
Install essential Python and JavaScript tools:
```
sudo apt install python3-dev python3-pip python3-venv npm
```

### Install the sbctl tool
Install SituationBoard's command line tool and enable bash auto completion.
```
sudo ln -sf "$PWD/sbctl" /usr/bin/sbctl
sudo ln -sf "$PWD/sbctl" /etc/bash_completion.d/sbctl
```

### Install the sbctl man page
Install the man page for the sbctl tool.
```
ln -sf "$PWD/misc/setup/sbctl.1" /usr/local/share/man/man1/sbctl.1
```
Then update the man page database.
```
sudo mandb --quiet
```

### Setup Python environment
Create a new Python environment and update important tools:
```
python3 -m venv ./venv
./venv/bin/pip3 install --upgrade pip setuptools wheel
```

### Install Python dependencies
Install the Python dependencies that are listed in the ```misc/setup/requirements.txt``` file:
```
./venv/bin/pip3 install -r misc/setup/requirements.txt
```

### Install JavaScript dependencies
Install the JavaScript dependencies that are listed in the ```frontend/package.json``` file:
```
npm install --only=production --prefix frontend/
```

### Copy the default configuration
Copy the file  ```misc/setup/situationboard_default.conf``` to  ```situationboard.conf ``` and adjust the [Configuration](Configuration.md).
```
cp misc/setup/situationboard_default.conf situationboard.conf
```

### Mark SituationBoard as installed
Create the file ```.installed``` and add a line with the feature ```BASE``` to it:
```
touch ".installed"
echo "base" >> ".installed"
```


## GPIO Support (requires Raspberry Pi)

### Install required Python library
Install the GPIO libraries for the Raspberry Pi:
```
./venv/bin/pip3 install rpi-lgpio lgpio
```

### Mark GPIO feature as installed
Add a line with the feature ```GPIO``` to the file ```.installed```:
```
echo "gpio" >> ".installed"
```


## SMS Support (requires a modem)

### Install GAMMU
Install GAMMU as interface to the modem and to receive SMS:
```
sudo apt install gammu libgammu-dev
```

### Install GAMMU Python library
Install Python library to interact with GAMMU:
```
./venv/bin/pip3 install python-gammu
```

### Configure GAMMU
Copy the file ```misc/setup/gammu-smsdrc``` to ```/etc/gammu-smsdrc``` and adjust it according to your needs.
```
sudo cp misc/setup/gammu-smsdrc /etc/gammu-smsdrc
```
Specifically, replace the line ```__SBPIN_LINE__``` with ```pin = <YOUR_SIM_PIN>``` if a PIN is required or remove the line entirely.
Furthermore, replace ```__SBDEVICE_LINE__``` with ```device = <YOUR_MODEM_DEVICE>``` (e.g. ```device = /dev/ttyUSB0```) and
```__SBCONNECTION_LINE__``` with ```connection = <YOUR_MODEM_CONNECTION>``` (e.g. ```connection = at```).

### Install UDEV rules
Install UDEV rules for the modem:
```
sudo cp misc/setup/50-situationboard-ttyUSB.rules /etc/udev/rules.d/
```
Afterwards, replace ```__SBDEVICE__``` with your modem device (e.g. ```ttyUSB0```)
and ```__SBSERVICE__``` with ```situationboard.service```.

### Setup USB modeswitch
Install and configure USB modeswitch as a workaround for some E303 modems:
```
sudo apt install usb-modeswitch usb-modeswitch-data
sudo cp misc/setup/12d1:1f01 /usr/share/usb_modeswitch/
```

### Mark SMS feature as installed
Add a line with the feature ```SMS``` to the file ```.installed```:
```
echo "sms" >> ".installed"
```


## Autostart Support (required for production use)

### Install SituationBoard systemd service
Copy the file ```misc/setup/situationboard.service``` to ```/etc/systemd/system/situationboard.service```
```
sudo cp misc/setup/situationboard.service /etc/systemd/system/situationboard.service
```
Replace the ```__SBPATH__``` placeholders with the path to your SituationBoard folder and
the placeholders for ```__SBUSER__``` and ```__SBDEVICE__``` with the
desired SituationBoard user (e.g. ```pi```) and required devices (e.g. ```dev-ttyUSB0.device```).

Finally, reload the configuration:
```
sudo systemctl daemon-reload
```
You can later enable/start the service with ```sudo sbctl enable``` and ```sudo sbctl start``` after the installation is complete.

### Install CEC utils
Install CEC support to be able to turn displays on in case of an alarm:
```
sudo apt install cec-utils
```

### Setup unclutter to hide the cursor
Install unclutter by executing the command:
```
sudo apt install unclutter
```

### Setup browser autostart
To open a browser with the SituationBoard frontend in full-screen on system startup
copy the script ```misc/setup/SituationBoardFrontend.desktop```
to ```/home/<USERNAME>/.config/autostart/SituationBoardFrontend.desktop```:
```
mkdir -p /home/<USERNAME>/.config/autostart/
cp misc/setup/SituationBoardFrontend.desktop /home/<USERNAME>/.config/autostart/SituationBoardFrontend.desktop
```

### Mark AUTOSTART feature as installed
Add a line with the feature ```AUTOSTART``` to the file ```.installed```:
```
echo "autostart" >> ".installed"
```


## Test Support (required for development)

### Install test tools
Install the tidy tool that allows automatic validation of HTML code
and shellcheck for automatic validation of shell files:
```
sudo apt install tidy shellcheck
```

### Install Python test dependencies
Install Python dependencies for automatic code validation and unit tests:
```
./venv/bin/pip3 install -r misc/setup/dev-requirements.txt
```

### Install JavaScript test dependencies
Install JavaScript dependencies for automatic code validation:
```
npm install --only=development --prefix frontend/
```

### Mark TEST feature as installed
Add a line with the feature ```TEST``` to the file ```.installed```:
```
echo "test" >> ".installed"
```
