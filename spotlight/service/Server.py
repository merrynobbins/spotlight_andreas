from spotlight.service.session.SpotifyCallbacks import SpotifyCallbacks  
from spotlight.service.session.SessionFactory import SessionFactory
from spotlight.service.session.MainLoopThread import MainLoopThread
from spotlight.service.LocalService import LocalService
from spotlight.service.session.Authenticator import Authenticator
from spotlight.service.session.ProxyInfo import ProxyInfo
from spotlight.service.util.UrlGenerator import UrlGenerator
from spotlight.service.util.ModelFactory import ModelFactory
from spotifyproxy.audio import BufferManager
from spotify import MainLoop
from spotifyproxy.httpproxy import ProxyRunner
from SimpleXMLRPCServer import SimpleXMLRPCServer
from spotlight.model.Settings import Settings
from spotlight.service.ShutdownWatcher import ShutdownWatcher

class Server:

    def __init__(self):
        self.settings = Settings()
        self.buffer_manager = BufferManager()
        self.authenticator = Authenticator()
        self.main_loop = MainLoop()

    def start(self):        
        self.session = self.set_up_session()
        self.runner = self.start_main_loop()        
        self.start_proxy_runner()
        self.log_in()
        self.install_shutdown_watcher()
        self.start_rpc_server()
        
    def stop(self):
        self.session.logout()
        self.server.shutdown()
        self.runner.stop()
        self.proxy_runner.stop()

    def start_main_loop(self):
        runner = MainLoopThread(self.main_loop, self.session)
        runner.start()
        return runner

    def start_proxy_runner(self):
        self.proxy_runner = ProxyRunner(self.session, self.buffer_manager, host='127.0.0.1', allow_ranges=False)
        self.proxy_runner.start()
        self.proxy_info = ProxyInfo(self.proxy_runner)
        return self.proxy_info

    def start_rpc_server(self):
        model_factory = self.create_model_factory(self.session, self.proxy_info)
        self.server = SimpleXMLRPCServer(("localhost", self.settings.internal_server_port))
        self.server.register_instance(LocalService(self.session, self.authenticator, model_factory))        
        self.server.serve_forever()      

    def install_shutdown_watcher(self):
        ShutdownWatcher(self).start()

    def set_up_session(self):
        callbacks = SpotifyCallbacks(self.main_loop, self.buffer_manager, self.authenticator)
        session = SessionFactory(callbacks, self.settings).create_session()
        self.set_up_authenticator(session)
        return session

    def set_up_authenticator(self, session):
        return self.authenticator.set_session(session)

    def log_in(self):
        return self.authenticator.login(self.settings.username, self.settings.password)

    def create_model_factory(self, session, proxy_info):
        url_gen = UrlGenerator(session, proxy_info)
        model_factory = ModelFactory(url_gen)
        return model_factory
    
        
