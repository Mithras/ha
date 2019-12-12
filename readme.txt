* telegram_bot
    * https://api.telegram.org/bot{api_key}/getUpdates
* wake_on_lan
    1. BIOS:
        APM Configuration\ErP Ready: DISABLED
        APM Configuration\Power on by PCI-E: ENABLED
    2. Device Manager -> NetworkAdapter
        Power Management
            Check everything
        Advanced
            Enable PME: true
            Energy Efficient Ethernet: false
            Reduce Speed On Power Down: false
            System Power Saver: false
            System Idle Power Saver: false
            Ultra low power mode: false
    3. Power Options
        Fast Startup: false
* RPC Shutdown
    1. Autostart "RemoteRegistry" service
    2. Disable the Firewall
    3. HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
        LocalAccountTokenFilterPolicy = 1 (DWORD 32-bit)
* mosquitto
    * mosquitto_pub -h <host> -p <port> -u <user> -P <password> -t <topic_to_remove> -n -r -d
* HUSBZB-1 (bottom usb 2.0)
    /dev/ttyUSB0 # z-wave
    /dev/ttyUSB1 # zigbee
* ConBee II (top usb 2.0)
    /dev/ttyACM0
* Deconz
    * Change a specific sensor name
        # deconz.configure
        field: /sensors/4
        data:
          name: Mi Magic Cube 01 (Analog)
* owntracks
    TODO
