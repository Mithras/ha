* telegram_bot
    * https://api.telegram.org/bot{api_key}/getUpdates
* wake_on_lan
    1. BIOS:
        APM Configuration\ErP Ready: DISABLED
        APM Configuration\Power on by PCI-E: ENABLED
    2. Device Manager -> NetworkAdapter
        2.1 Update driver
        2.2 Power Management
            Check everything
        2.3 Advanced
            Enable PME: Enabled
            Wake on Magic Packet: Enabled
    3. Power Options
        Fast Startup: false
* RPC Shutdown
    1. Autostart "RemoteRegistry" service
    2. Disable the Windows Defender or
        2.1 Allow an app or feature through Windows Defender Firewall
            Remote Service Management
            Remote Shutdown
            Windows Management Instrumentation (WMI)
        2.2 netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow profile=private
    3. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
        LocalAccountTokenFilterPolicy = 1 (DWORD 32-bit)
* mosquitto
    * mosquitto_pub -h <host> -p <port> -u <user> -P <password> -t <topic_to_remove> -n -r -d
* HUSBZB-1 (bottom usb 2.0)
    /dev/ttyUSB0 # z-wave
    /dev/ttyUSB1 # zigbee
* ConBee II (top usb 2.0)
    /dev/ttyACM0
    /dev/serial/by-id/usb-dresden_elektronik_ingenieurtechnik_GmbH_ConBee_II_DE2120244-if00
* Deconz
    * Change a specific sensor name
        # deconz.configure
        field: /sensors/4
        data:
          name: Mi Magic Cube 01 (Analog)
* owntracks
    owntracks/<user>/<device>/cmd
    {
        "_type": "configuration",
        "locatorDisplacement": 100,
        "locatorInterval": 60,
        "mqttProtocolLevel": 4
    }
* VS Code Remote - SSH
    * Permissions (root@hassio)
        chmod o+w -R /config # https://ss64.com/bash/chmod.html
    * Git (pi@hassio)
        sudo apt install git-all # BUG: git-all removes "network-manager". Try "sudo apt install git" instead?
        git config --global core.autocrlf true
        git config --global user.name "Mithras"
    * Pip, pylint, autopep8 (pi@hassio)
        sudo apt-get install python3-pip
        ls /usr/bin/python*
        alias py='/usr/bin/python3'
        py -V
        py -m pip install pylint
        py -m pip install autopep8
    * .ssh/config
        Host raspberry
        HostName hassio
        User pi
        Port 22
        IdentityFile ~/.ssh/raspberry_rsa
