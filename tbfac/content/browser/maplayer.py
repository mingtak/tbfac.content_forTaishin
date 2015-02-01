from plone.memoize.instance import memoizedproperty
from collective.geo.mapwidget.maplayers import MapLayer
from collective.geo.mapwidget.browser.widget import MapLayers


class KMLMapLayer(MapLayer):
    """map layer see: collective.geo.mapwidget
    """
    name = 'infovenuesmap'

    @memoizedproperty
    def jsfactory(self):
        title = self.context.Title().replace("'", "\'")
        if isinstance(title, str):
            title = title.decode('utf-8')
        url = self.context.absolute_url()
        if not url.endswith('/'):
            url += '/'
        template = self.context.restrictedTraverse('%s-layer' % self.name)()
        return template % (title, url)

class KMLMapLayers(MapLayers):
    """Create all layers for IInfoVenuesMapView.
    """

    def layers(self):
        layers = super(KMLMapLayers, self).layers()
        layers.append(KMLMapLayer(context=self.context))
        return layers
