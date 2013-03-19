'''
freeseer - vga/presentation capture software

Copyright (C) 2011-2012  Free and Open Source Software Learning Centre
http://fosslc.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

For support, questions, suggestions or any other inquiries, visit:
http://wiki.github.com/Freeseer/freeseer/

@author: Thanh Ha
@author: Olivier Gauthier
'''

import ConfigParser

import pygst
pygst.require("0.10")
import gst

from PyQt4 import QtGui, QtCore

from freeseer.framework.plugin import IVideoInput

class RTSPVideoSrc(IVideoInput):
    name = "RTSP video source"
    os = ["linux", "linux2", "win32", "cygwin", "darwin"]
    
    # variables
    url = "rtsp://127.0.0.1:8554/"
    #pattern = "smpte"
    
    # Patterns
    #PATTERNS = ["smpte", "snow", "black", "white", "red", "green", "blue",
    #            "circular", "blink", "smpte75", "zone-plate", "gamut",
    #            "chroma-zone-plate", "ball", "smpte100", "bar"]
    
    def on_pad_added(self, element, pad, data):
        #sinkpad = data.get_pad("sink")
        element.link(data)
    
    def get_videoinput_bin(self):
        bin = gst.Bin() # Do not pass a name so that we can load this input more than once.
                
        videosrc = gst.element_factory_make("rtspsrc", "videosrc")
        videosrc.set_property("location", self.url)
        demux = gst.element_factory_make("rtph264depay", "demux")
        decoder = gst.element_factory_make("ffdec_h264", "decoder")
        colorspace = gst.element_factory_make("ffmpegcolorspace", "colorspace")

        # Add elements
        bin.add(videosrc)
        bin.add(demux)
        bin.add(decoder)
        bin.add(colorspace)
        
        # Link elements
        #videosrc.link(demux)
        demux.link(decoder)
        decoder.link(colorspace)

        # Link videosrc to demux
        videosrc.connect("pad-added", self.on_pad_added, demux)
    
        # Setup ghost pad
        pad = colorspace.get_pad("src")
        ghostpad = gst.GhostPad("videosrc", pad)
        bin.add_pad(ghostpad)
        
        return bin

    
    def load_config(self, plugman):
        self.plugman = plugman
        
        try:
            #live = self.plugman.get_plugin_option(self.CATEGORY, self.get_config_name(), "Live")
            #if live == "True": self.live = True
            self.url = self.plugman.get_plugin_option(self.CATEGORY, self.get_config_name(), "Url")
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.plugman.set_plugin_option(self.CATEGORY, self.get_config_name(), "Url", self.url)
            #self.plugman.set_plugin_option(self.CATEGORY, self.get_config_name(), "Pattern", self.pattern)
        except TypeError:
            # Temp fix for issue where reading checkbox the 2nd time causes TypeError.
            pass
        
    def get_widget(self):
        if self.widget is None:
            self.widget = QtGui.QWidget()
            
            layout = QtGui.QVBoxLayout()
            self.widget.setLayout(layout)
            
            #
            # Settings
            #
            
            #self.liveCheckBox = QtGui.QCheckBox("Live Source")
            #layout.addWidget(self.liveCheckBox)
            
            formWidget = QtGui.QWidget()
            formLayout = QtGui.QFormLayout()
            formWidget.setLayout(formLayout)
            layout.addWidget(formWidget)
            
            self.urlLabel = QtGui.QLabel("RTSP url:")
            self.urlLineEdit = QtGui.QLineEdit()
            self.urlLabel.setBuddy(self.urlLineEdit)
            #for i in self.PATTERNS:
            #    self.patternComboBox.addItem(i)
            
            formLayout.addRow(self.urlLabel, self.urlLineEdit)
            
            #self.widget.connect(self.patternComboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.set_pattern)
            
        return self.widget

    def widget_load_config(self, plugman):
        self.load_config(plugman)
        
        self.urlLineEdit.setText(self.url)
        
    def set_url(self, url):
        self.url = url
        self.plugman.set_plugin_option(self.CATEGORY, self.get_config_name(), "Url", self.url)
        self.plugman.save()
        
    def get_properties(self):
        return ['Url']
    
    def get_property_value(self, property):
        if property == 'Url':
            return self.url
        #elif property == 'Pattern':
        #    return self.pattern
        else:
            return "There's no property with such name"
        
    def set_property_value(self, property, value):
        #if property == 'Live':
        #    if(value == "ON"):                
        #        self.set_live(True)
        #    elif(value == "OFF"):
        #        self.set_live(False)
        #   else:
        #       return "Please choose one of the acceptable variable values: ON or OFF"
        if property == "Url":
            self.set_url(value)            
        else:
            return "Error: There's no property with such name" 
        

