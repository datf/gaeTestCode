import os
import jinja2

class JinjaTemplate(object):
    """
    The JinjaTemplate class provides a wrapper of the jinja2 environment to load
    templates (AKA Views) from the 'templates' folder, adding the autoescape
    extension by default.
    """

    _jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
            '..', 'templates')),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)

    _template = None

    def __init__(self, name, parent=None, globs=None):
        """
        Constructs the template internally for the file specified by name,
        having (optionally) a parent template.
        The globs argument can be used to provide template-wide globals.
        """
        try:
            self._template = self._jinja_environment.get_template(
                name, parent, globs
                )
        except jinja2.TemplateNotFound as ex:
            raise JinjaTemplateNotFoundException(ex)

    def render(self, *args, **kwargs):
        """
        This method renders the template with the values passed as arguments in
        key-value format (dict). Ex:
            jinja_template.render(key=value, key2=value2)
            jinja_template.render({key=value, key2=value2})
        """
        return self._template.render(*args, **kwargs)

class JinjaTemplateNotFoundException(jinja2.TemplateNotFound):
    """
    Exception to present to users of this module instead of jinja2's
    """
    pass
