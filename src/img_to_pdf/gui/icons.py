"""Icon provider using FluentIcon."""

from qfluentwidgets import FluentIcon as FIF


class Icons:
    """Centralized icon access."""
    
    @staticmethod
    def home(): return FIF.HOME
    
    @staticmethod
    def settings(): return FIF.SETTING
    
    @staticmethod
    def add(): return FIF.ADD
    
    @staticmethod
    def delete(): return FIF.DELETE
    
    @staticmethod
    def folder(): return FIF.FOLDER
    
    @staticmethod
    def sync(): return FIF.SYNC
    
    @staticmethod
    def save(): return FIF.SAVE
    
    @staticmethod
    def photo(): return FIF.PHOTO
