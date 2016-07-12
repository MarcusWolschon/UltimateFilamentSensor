$(function() {
    function FilamentSensorViewModel(parameters) {
        var self = this;

        self.alarm    = ko.observable();
        self.weight   = ko.observable();
        self.force    = ko.observable();
        self.odometry = ko.observable();
        self.show_status = ko.observable(false);

        self.initialMessage = function(data) {
            self.alarm(data.alarm);
            self.weight(data.weight);
            self.force(data.force);
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

        self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "ultimate_filament_sensor") {
                return;
            }

            self.alarm(data.alarm);
            self.weight(data.weight);
            self.force(data.force);
            self.odometry(data.odometry);
            self.show_status(true);
        };
    }

    // This is how our plugin registers itself with the application, by adding some configuration
    // information to the global variable OCTOPRINT_VIEWMODELS
    // We bind this ViewModel to the UI-element defined in templates/ultimate_filament_sensor_sidebar.jinja2
    OCTOPRINT_VIEWMODELS.push([
        FilamentSensorViewModel,
        [ ],
        ["#sidebar_filament_sensor"]
    ]);
})
