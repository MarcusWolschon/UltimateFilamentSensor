$(function() {
    function FilamentSensorViewModel(parameters) {
        var self = this;

        self.alarm    = ko.observable();
        self.weight   = ko.observable();
        self.force    = ko.observable();
        self.force_min    = ko.observable();
        self.force_max    = ko.observable();
        self.odometry = ko.observable();
        self.show_status = ko.observable(false);

        self.initialMessage = function(data) {
            self.alarm(data.alarm);
            self.weight(data.weight);
            self.force(data.force);
            self.force_min(data.force_min);
            self.force_max(data.force_max);
            self.odometry(data.odometry);
            //self.show_status(data.odometry | data.weight | data.alarm | data.force ? true : false);
            self.show_status(true);
        };

        self.onStartupComplete = function() {
            // WebApp started, get message if any
            // ultimate_filament_sensor is the plugin-identifier from setup.py
            // __init__.py will get this via on_api_get() using the SimplyAPIPlugin -mixin
            $.ajax({
                url: API_BASEURL + "plugin/ultimate_filament_sensor",
                type: "GET",
                dataType: "json",
                success: self.initialMessage
            });
        }
 
        // Called when a plugin message is pushed from the server with the identifier of the calling plugin
        // as first and the actual message as the second parameter. Note that the latter might be a full
        // fledged object, depending on the plugin sending the message. You can use this method to
        // asynchronously push data from your plugin’s server component to it’s frontend component.
        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "ultimate_filament_sensor") {
                return;
            }

            self.alarm(data.alarm);
            self.weight(data.weight);
            self.force(data.force);
            self.force_min(data.force_min);
            self.force_max(data.force_max);
            self.odometry(data.odometry);
            self.show_status(true);
        };
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    // We bind this ViewModel to the div-element defined in templates/ultimate_filament_sensor_sidebar.jinja2
    OCTOPRINT_VIEWMODELS.push([
        FilamentSensorViewModel,
        [ ],
        ["#sidebar_filament_sensor"]
    ]);
})
