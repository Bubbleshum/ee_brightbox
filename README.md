# ee_brightbox
 eeSmarthub custom component for home assistant
 
 This custom component overwrites the ee_brightbox component to allow EE Smart Hubs to function with the device tracker component.
 
 Original ee_brightbox component can be found at https://github.com/home-assistant/core/tree/dev/homeassistant/components/ee_brightbox

Extra resources;
Krygal's eebrightbox https://github.com/krygal/eebrightbox </br>
Calmjs' Parse https://github.com/calmjs/calmjs.parse


Home Assistant Installation;
simply copy all these files into config/custom_components

Inside configuration.yaml enter the following to enable, then restart home assistant to load

```
 device_tracker:
 - platform: ee_brightbox
   host: 192.168.1.254
   password: YOUR_ROUTER_ADMIN_PASSWORD
   new_device_defaults:
     track_new_devices: true
```
