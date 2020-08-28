#!/usr/bin/env python3

import logging

from configator.engine import RedisClient
from configator.utils.function import json_dumps
from typing import List, Tuple, Dict, Optional, Union

LOG = logging.getLogger(__name__)

class SettingPublisher(RedisClient):
    #
    def __init__(self, *args, **kwargs):
        super(SettingPublisher, self).__init__(**kwargs)
        self.CHANNEL_PREFIX = self.CHANNEL_GROUP + ':'
    #
    #
    def publish(self, message: Union[Dict, bytes, str, int, float],
            label: Optional[Union[bytes,str]] = None,
            with_datetime: Optional[bool] = False):
        try:
            self.publish_or_error(message, label=label, with_datetime=with_datetime)
            return None
        except Exception as err:
            return err
    #
    #
    def publish_or_error(self, message: Union[Dict, bytes, str, int, float],
            label: Optional[Union[bytes,str]] = None,
            with_datetime: Optional[bool] = False):
        if label is None:
            channel_name = self.CHANNEL_GROUP
        else:
            if isinstance(label, bytes):
                label = label.decode('utf-8')
            else:
                label = str(label)
            channel_name = self.CHANNEL_PREFIX + label
        #
        if isinstance(message, dict):
            message, err = json_dumps(message, with_datetime=with_datetime)
            if err:
                if LOG.isEnabledFor(logging.ERROR):
                    LOG.log(logging.ERROR, err)
                raise err
        elif not self.__is_valid_type(message):
            errmsg = "Invalid type of input: '%s'. Only a dict, bytes, string, int or float accepted." % type(message)
            if LOG.isEnabledFor(logging.ERROR):
                LOG.log(logging.ERROR, errmsg)
            raise ValueError(errmsg)
        #
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.log(logging.DEBUG, "publish() a message [%s] to channel [%s]", str(message), channel_name)
        #
        self.connect().publish(channel_name, message)
    #
    #
    def close(self):
        super().close()
        if LOG.isEnabledFor(logging.DEBUG):
            LOG.log(logging.DEBUG, "SettingPublisher has closed")
    #
    #
    @staticmethod
    def __is_valid_type(data):
        return isinstance(data, (bytes, str, float)) or (isinstance(data, int) and (type(data) != type(True)))
