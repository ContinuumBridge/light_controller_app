# light_controller_app
A bridge app for controlling RGBW LED bulbs with warm and cool color temperature white LEDs.
In this first version, it does the following:

* Connects to a single LED bulb that supports RGB, daylight white and warm white.
* Connects to a switch or keyfob that has four buttons. Two are used to conntrol brightness and two cycle through the colours: daylight white, warm white, red, green and blue.
* Looks for a file in the thisbridge directory called circadian.json and uses this to switch between daylight and warm white at the specified times of day. Here is an example of the file format:

    {
        "ontimes": 
        [
            "Mon 06:30",
            "Tue 06:30",
            "Wed 06:30",
            "Thu 06:30",
            "Fri 06:30",
            "Sat 06:30",
            "Sun 06:30"
        ],
        "offtimes":
        [
            "Mon 19:30",
            "Tue 19:30",
            "Wed 19:30",
            "Thu 19:30",
            "Fri 19:30",
            "Sat 19:30",
            "Sun 19:30"
        ]
    }

This example has one on and one off time per day, but there can be as many as you like.
