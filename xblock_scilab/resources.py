from django.template import Context, Template

import pkg_resources


# This probably needs to be in separate shared package
class XBlockResources(object):

    package = __package__

    def render_template(self, template_path, context=None, package_name=None):
        """
        Evaluate a template by resource path, applying the provided context
        """
        if context is None:
            context = {}
        if package_name is None:
            package_name = self.package
        template_str = self.load_resource(template_path, package_name=package_name)
        template = Template(template_str)
        return template.render(Context(context))

    def load_resource(self, resource_path, package_name=None):
        """
        Gets the content of a resource
        """
        if package_name is None:
            package_name = self.package
        resource_content = pkg_resources.resource_string(package_name, resource_path)
        return resource_content
        # return unicode(resource_content)

    def resource_string(self, path, package_name=None):
        """Handy helper for getting resources from our kit."""
        if package_name is None:
            package_name = self.package
        data = pkg_resources.resource_string(package_name, path)
        return data
        # return data.decode("utf8")

    def load_js(self, js_name, package=None):
        js_name = 'resources/javascript/%s' % js_name
        return self.load_resource(js_name, package)

    def load_template(self, template_name, context=None, package=None):
        template_name = 'resources/templates/%s' % template_name
        return self.render_template(template_name, context, package)

    def load_css(self, css_name, package=None):
        css_name = 'resources/styles/%s' % css_name
        return self.load_resource(css_name, package)