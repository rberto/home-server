from  netstatus import netstatus
import inspect

"""
Declare here all action a user can call.
Use docstring of function to add short description.
All action and descriptions listed via the list_actions method.
"""
class actions():

    def wake_media_center(self):
        """ Wake media center. """
        netstatus().wake_on_lan(netstatus.MEDIA_CENTER_MAC)
        return "Done"

    def shutdown_media_center(self):
        """ Shutdown media center."""
        return netstatus().shutdown(netstatus.MEDIA_CENTER_IP)

    def shutdown_all(self):
        """ ShutDown all device"""
        ips = ""
        for ip in netstatus().find_listening_devices(netstatus.SHUTDOWN_PORT):
            netstatus().shutdown(ip)
            ips = ips + str(ip) + ";"
        return ips
        

    def list_actions(self):
        """ 
        Get list of all the actions available. With its description
        Resutl will not contain this method.
        """
        actionlist = []
        for method_tuple in inspect.getmembers(actions, predicate=inspect.ismethod):
            if method_tuple[0] != "list_actions":
                doc = inspect.getdoc(getattr(actions, method_tuple[0]))
                result = dict()
                result["title"] = method_tuple[0]
                result["description"] = doc
                actionlist.append(result)
        return actionlist

if __name__ == "__main__":
    print actions().list_actions()
