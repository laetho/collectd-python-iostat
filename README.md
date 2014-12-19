collectd-python-iostat
======================

collectd-python-iostat is a Python plugin for collectd that parse Linux iostat output and enable graphing in graphite or other output formats.

The plugin is based on information gleaned from [deniszh's collectd-iostat-python](https://github.com/deniszh/collectd-iostat-python) but his project contains no actual code. This readme also contain information adapted from deniszh's project.



Status
------

The state of the plugin can be considered proof-of-concept. The code works for me, but needs some more work to become more mature and generic. As an example the config options are not really used for anything yet.


Setup
-------
Deploy the collectd python plugin into a suitable plugin directory for your collectd instance.

Configure collectd's python plugin to execute the iostat plugin using a stanza similar to the following:


    <LoadPlugin python>
        Globals true
    </LoadPlugin>

    <Plugin python>
        ModulePath "/usr/lib/collectd/plugins/python"
        Import "collectd_iostat_python"

        <Module collectd_iostat_python>
            Path "/usr/bin/iostat"
            Interval 10
            Verbose False
        </Module>
    </Plugin>

Once functioning, the iostat data should then be visible via your various output plugins.

In the case of Graphite, collectd should be writing data to graphite in the *hostname_domain_tld.iostat.DEVICE.gauge.column-name* style.



Contact
-------
[Email - Lars Erik Thorsplass](mailto:thorsplass@gmail.com)
