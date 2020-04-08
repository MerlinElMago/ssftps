#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Stupidly Sipmple FTP Server by D.Sánchez
# This program is published under the EU-GPL, get your copy at
# https://joinup.ec.europa.eu/sites/default/files/custom-page/attachment/eupl_v1.2_en.pdf
# Based on the GTK3 Library in pyGObject for python and driven by pyftpdlib by
# Giampaolo Rodola - https://github.com/giampaolo/pyftpdlib.
# You may install the dependencies with sudo apt-get install python3-pyftpdlib

import gi, os, threading, logging
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

class FTP_Server:
    """
        A FTP Server Class to be launched whithin a non blocking thread
    """
    #Declare version number of the server-class
    cVersion = "1.0-4"

    #Class constructor
    def __init__( self ):
        #Create an atuhorizer...
        self.cAuthorizer = DummyAuthorizer()
        #Create a FTPHandler ( required for FTPServer )
        self.cHandler = FTPHandler
        #Create a FTPAuthorizer ( required for FTPServer )
        self.cHandler.authorizer = self.cAuthorizer
        #Establish a default banner ( optional )
        self.cHandler.banner = "ssftps server v" + self.cVersion + " ready."

    def run( self ):
        #Is the user list empty?
        if not myConfig.USERS:
            #YES - Activate the anonymous login
            self.cAuthorizer.add_anonymous( os.getcwd() )
        else:
            #NO - Iterate over userlist
            for tmpUser in myConfig.USERS:
                self.cAuthorizer.add_user( tmpUser['user'], tmpUser['pass'], tmpUser['path'] )
        #Instantiate FTPServer
        self.cServer = FTPServer( ( myConfig.IPV4, myConfig.PORT ) , self.cHandler )
        #Run the server
        self.cServer.serve_forever()

    def stop( self ):
        #Stop the server
        self.cServer.close_all()

    def add_user( self, tmpUser,tmpPasswd, tmpPath, tmpPrivileges='elradfmwMT' ):
        #Add a user with all read write priveleges, unless otherwise specified
        self.authorizer.add_user( str( tmpUser ), str( tmpPasswd ), str( tmpPath ), perm=str( tmpPrivileges ) )
        #Check out permissions at https://pyftpdlib.readthedocs.io/en/latest/api.html#pyftpdlib.authorizers.DummyAuthorizer

class MainWindow(Gtk.Window):
    """
        This class defines the main window of the application
    """
    def __init__(self):
        #Configure Main Window
        Gtk.Window.__init__(self, title="ssftps")
        self.set_border_width( 5 )
        self.set_default_size( 600, 400 )
        #Configure a Headerbar
        cHeaderBar = Gtk.HeaderBar()
        cHeaderBar.set_show_close_button(True)
        cHeaderBar.props.title = "Stupidly Simple FTP Server v" + FTP_Server.cVersion
        self.set_titlebar(cHeaderBar)
        #Button for Headerbar
        myConfigButton = Gtk.Button()
        myConfigButton.props.relief = Gtk.ReliefStyle.NONE
        myConfigButton.add( Gtk.Image.new_from_gicon( Gio.ThemedIcon( name="emblem-system-symbolic" ), Gtk.IconSize.BUTTON ) )
        myConfigButton.connect( "clicked", self.configButtonClicked )
        #Create a switch for the headerbar
        onoffSwitch = Gtk.Switch()
        onoffSwitch.props.valign = Gtk.Align.CENTER
        onoffSwitch.connect( "state-set", self.onoffSwitchChanged )
        #Pack everything
        cHeaderBar.pack_end( onoffSwitch )
        cHeaderBar.pack_end( myConfigButton )
        #Create a scrollable container for the TextView
        myScroller = Gtk.ScrolledWindow()
        myScroller.set_border_width( 2 )
        myScroller.set_policy( Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC )
        #Create a Textview
        myTextView = Gtk.TextView()
        myTextView.set_editable( False )
        #Declare a class level TextBuffer to log to.
        self.cTextBuffer = myTextView.get_buffer()
        #Put it all into our scrollable container
        myScroller.add( myTextView )
        self.add( myScroller )
        #Create all entry boxes for the port, username, password and directory
        self.cEntryPORT = Gtk.Entry()
        self.cEntryPORT.set_text( myConfig.PORT )
        self.cEntryUSER = Gtk.Entry()
        self.cEntryPASS = Gtk.Entry()
        self.cEntryPATH = Gtk.Entry()

        if not myConfig.USERS:
            self.cEntryUSER.set_text( 'anonymous' )
            self.cEntryPASS.set_text( '' )
            self.cEntryPATH.set_text( '.' )
        else:
            self.cEntryUSER.set_text( myConfig.USERS[0]['user'] )
            self.cEntryPASS.set_text( myConfig.USERS[0]['pass'] )
            self.cEntryPATH.set_text( myConfig.USERS[0]['path'] )
        self.cEntryPASS.set_visibility( False ) #This will make it a password input
        self.cEntryPATH.set_editable( False ) #We only want to permit walid paths, so we just make it non-editable
        self.cEntryPATH.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "folder");
        self.cEntryPATH.connect( "icon-press", self.openFileDialogFromPopover )
        #Create a Popover
        self.cPopover = Gtk.Popover()
        self.cPopover.set_border_width( 10 )
        #Put all element inside a Box
        verticalBox = Gtk.Box( orientation=Gtk.Orientation.VERTICAL )
        verticalBox.pack_start( Gtk.Label("Port"), False, True, 3 )
        verticalBox.pack_start( self.cEntryPORT, False, True, 3 )
        verticalBox.pack_start( Gtk.Label("Username"), False, True, 3 )
        verticalBox.pack_start( self.cEntryUSER, False, True, 10 )
        verticalBox.pack_start( Gtk.Label("Password"), False, True, 3 )
        verticalBox.pack_start( self.cEntryPASS, False, True, 3 )
        verticalBox.pack_start( Gtk.Label("Path"), False, True, 3 )
        verticalBox.pack_start( self.cEntryPATH, False, True, 3 )
        #Pack the boxk into out Popover
        self.cPopover.add( verticalBox )
        self.cPopover.connect( "closed", self.popoverClosed )
        self.cPopover.set_position(Gtk.PositionType.BOTTOM)

    def openFileDialogFromPopover( self, widget, icon_pos, event ):
        #Define the dialog to be opened
        myFileDialog = Gtk.FileChooserDialog("Select a root directory for the FTP server",
                                        self,
                                        Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        #Launch the dialog and capture it's output
        tmpResponse = myFileDialog.run()
        #Did the user accept the dialog?
        if tmpResponse == Gtk.ResponseType.OK:
            #YES - Write it to the entry box
            self.cEntryPATH.set_text( str( myFileDialog.get_filename() ) )
        #Destroy the dialog
        myFileDialog.destroy()

    def popoverClosed( self, widget ):
        #When the popover closes, all values are stored into the config
        #Has the username been changed?
        if self.cEntryUSER.get_text() != 'anonymous':
            #YES - Add the new user to the USERS list
            myConfig.USERS.append( {'user': self.cEntryUSER.get_text() , 'pass': self.cEntryPASS.get_text(), 'path': self.cEntryPATH.get_text()} )
        #Has the port value been changed?
        if self.cEntryPORT.get_text()!=myConfig.PORT:
            #YES - Save the new port (no error checking is done here)
            myConfig.PORT = self.cEntryPORT.get_text()
        self.cTextBuffer.insert( self.cTextBuffer.get_end_iter(), ">>> Applying new configuration <<<\n" )

    def logToTextBuffer( self, tmpMessage ):
        #Insert the logged text into the local textbuffer
        self.cTextBuffer.insert( self.cTextBuffer.get_end_iter(), tmpMessage+"\n" )

    def configButtonClicked( self, widget ):
        #Position the popover
        self.cPopover.set_relative_to( widget )
        #Show it...
        self.cPopover.show_all()
        self.cPopover.popup()

    def onoffSwitchChanged( self, widget, state ):
        #Is the server to be switchen on?
        if state==True:
            #YES - Instantiate the server
            self.cServer = FTP_Server()
            #Put it into a thread and configure it...
            self.cThread = threading.Thread( target=self.cServer.run )
            #... as a daemon
            self.cThread.daemon = True
            #Start the server-thread
            self.cThread.start()
        else:
            #NO - Inform the user that we are stopping the server
            self.cTextBuffer.insert( self.cTextBuffer.get_end_iter(), ">>> stopping FTP server on "+myConfig.IPV4+":"+myConfig.PORT+" <<<\n" )
            #Stop it!
            self.cServer.stop()

class LogHandler(logging.Handler):
    """
        This is a redefined class from logging.Handler with the emit method overridden.
    """
    def __init__(self, tmpTextBuffer ):
        #Initialize the superclass
        super(LogHandler, self).__init__()
        #Capture the TextBuffer
        self.cTextBuffer = tmpTextBuffer

    def emit( self, tmpMessage ):
        #Store the formattet message
        tmpMessage = self.format( tmpMessage )
        #Wait GTK to be idle and print log message
        GObject.idle_add(self.cTextBuffer.insert, self.cTextBuffer.get_end_iter(), tmpMessage + "\n")
        #Send the log message to the textbuffer
        #self.cTextBuffer.insert( self.cTextBuffer.get_end_iter(), tmpMessage + "\n" )

class ServerConfiguration():
    """
        This class holds the server configuration
    """
    def __init__(self):
        #This reads the private IP address from all interfaces and chooses the first one (this should work in most cases)
        self.IPV4 = os.popen('hostname --all-ip-addresses | cut -d " " -f1').read().rstrip("\n\r")
        #We define a default port which is available to the user (port 21 can't be listened on by the unprivileged user)
        self.PORT = "2121"
        #Default loglevel.
        self.LOGLEVEL = logging.DEBUG
        #Although only one user van be defined through the interface, you may add more "default users here"
        #This is a list containing a dictionary with the following items: {'user':'','pass':'','path':}
        #All users of this table, are added with FULL PRIVILEGES!
        self.USERS = []


#Declare the configuration container as a global variable (not elegant, but the only way I found)
global myConfig

#Create configuration Class
myConfig = ServerConfiguration()

#Create Main Window
myWindow = MainWindow()

#Connect the destroy signal to the main loop quit function
myWindow.connect("destroy", Gtk.main_quit)

#Print the welcome message
myWindow.cTextBuffer.set_text( "================\n" + "  ssftps Version " + FTP_Server.cVersion + "\n================\nPublished under the EU-GPL\n© 2020 D.Sánchez\nhttps://www.dsanchez.net/\n" )

#Configure log level
logging.basicConfig(level=myConfig.LOGLEVEL)

#Create a handler to control the log-message output
myHandler = LogHandler( myWindow.cTextBuffer )

#Link the handler to default logger
logging.getLogger('pyftpdlib').addHandler(myHandler)

#Show Windows on screen
myWindow.show_all()

#Main Loop
Gtk.main()
