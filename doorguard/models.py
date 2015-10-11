from django.db import models


class Config(models.Model):
    CONFIG_TYPES = (
        ('ALARM', 'Alarm-Type'),
        ('EMAIL', 'Email address'),
        ('CHECKER', 'Configuration for checker.py'),
    )
    config_type = models.CharField(max_length=10, choices=CONFIG_TYPES)
    name = models.CharField(max_length=100, blank=True)
    value = models.CharField(max_length=100, blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("config_type", "name")
        ordering = ['config_type', 'name', 'value']

    def __str__(self):
        return '{}, {}:{}'.format(self.config_type, self.name, self.value)

class Person(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Device(models.Model):
    name = models.CharField(max_length=50, unique=True)
    owner = models.ForeignKey(Person, null=True, blank=True)
    ip = models.GenericIPAddressField(protocol='ipv4', unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    is_home = models.BooleanField(default=False)

    def __str__(self):
        if self.owner:
            return '{} ({})'.format(self.owner.name, self.name)
        else:
            return '{}'.format(self.name)


class Log(models.Model):
    LOG_TYPES = (
        ('AL', 'Alarm'),
        ('DE', 'Device'),
        ('DO', 'Door'),
    )

    log_type = models.CharField(max_length=10, choices=LOG_TYPES)
    # status for Device: True when coming home, false when going
    # status for Door: True when closed, False when open
    status = models.BooleanField(default=True)
    device = models.ForeignKey(Device, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        s = ''
        if self.log_type == 'DO':
            if self.status:
                s = 'Door was closed'
            else:
                s = 'Door was opened'
        elif self.log_type == 'DE' and self.device:
            if self.status:
                s = '{} came home'.format(self.device)
            else:
                s = '{} went away...'.format(self.device)
        elif self.log_type == 'AL':
            s = 'ALAAAARM ALARM ALARM!!!'

        if self.text:
            s = s + ' ' + self.text
        return s
