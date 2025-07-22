# Office PC

runs a simple login mask that shows content depening on location and language selection
can be configured to run either a hh or s configuration in start.sh

## install and automati setup

move to the install folder then run following commands

```shell
chmod +x install.sh
chmod +x start.sh

./install.sh
```

then test via start.sh, also set the location as needed [s/hh] 

```shell
./start.sh
```

to setup an autostart open crontab `crontab -e`

`@reboot sleep 15 && ~/Office/start.sh >> out.txt  2>&1`
