import sys
import Globals
from os import path

cmfplone_globals=globals()
this_module = sys.modules[ __name__ ]

# Stores the available 'Customization Policies'
custom_policies={} 

ADD_CONTENT_PERMISSION = 'Add portal content'

misc_ = {'plone_icon': Globals.ImageFile(path.join('skins','plone_images','logoIcon.gif'), cmfplone_globals)}

# For plone_debug method
import zLOG
def log(message,summary='',severity=0):
    zLOG.LOG('MyDebugLog',severity,summary,message)

def transaction_note(note):
    """ Write human legible note """
    T=get_transaction()
    T.note(str(note))


def initialize(context):

    # Stuff has been moved from module level to this method for a
    # better separation of import and installation.
    # For the general user this change does not make a difference.
    # For test authors (and people who use parts of Plone only)
    # it does speed up import *significantly*.

    from AccessControl import ModuleSecurityInfo, ClassSecurityInfo
    from AccessControl import allow_module, allow_class, allow_type

    ModuleSecurityInfo('zLOG').declarePublic('LOG')
    ModuleSecurityInfo('zLOG').declarePublic('INFO')

    import StatelessTreeNav
    from StatelessTree import NavigationTreeViewBuilder
    allow_class(NavigationTreeViewBuilder)

    # For form validation bits
    from PloneUtilities import IndexIterator
    allow_class(IndexIterator)

    # Make IndexIterator available at module level
    this_module.IndexIterator = IndexIterator

    # For content_status_modify
    from Products.CMFCore.WorkflowCore import ObjectMoved, ObjectDeleted, WorkflowException
    ModuleSecurityInfo('WorkflowCore').declarePublic('ObjectMoved')
    ModuleSecurityInfo('WorkflowCore').declarePublic('ObjectDeleted')
    ModuleSecurityInfo('WorkflowCore').declarePublic('WorkflowException')
    allow_class(ObjectMoved)
    allow_class(ObjectDeleted)
    allow_class(WorkflowException)

    from PloneBatch import Batch
    allow_class(Batch)

    # Make Batch available at module level
    this_module.Batch = Batch

    from StringIO import StringIO
    allow_class(StringIO)

    ModuleSecurityInfo('Products.CMFPlone').declarePublic('transaction_note')
    ModuleSecurityInfo('Products.CMFPlone.Portal').declarePublic('listPolicies')

    ModuleSecurityInfo('Products.Formulator').declarePublic('StringField','EmailField')
    ModuleSecurityInfo('Products.Formulator.Form').declarePublic('FormValidationError', 'BasicForm')

    from Products.Formulator.StandardFields import StringField, EmailField
    from Products.Formulator.Form import FormValidationError, BasicForm
    allow_class(StringField)
    allow_class(EmailField)
    allow_class(FormValidationError)
    allow_class(BasicForm)

    # Setup ZODB if needed
    import PloneInitialize

    # Setup migrations
    import migrations
    migrations.registerMigrations()

    import setup
    import imagePatch

    from Products.CMFCore import DirectoryView
    DirectoryView.registerDirectory('skins', cmfplone_globals)

    import PloneFolder, PloneWorkflow, FolderWorkflow

    contentClasses = ( PloneFolder.PloneFolder , )
    contentConstructors = ( PloneFolder.addPloneFolder, )
    ftis = (PloneFolder.factory_type_information, )

    try:
        import LargePloneFolder
    except ImportError:
        pass
    else:
        contentClasses += ( LargePloneFolder.LargePloneFolder, )
        contentConstructors += ( LargePloneFolder.addLargePloneFolder,)
        ftis += (LargePloneFolder.factory_type_information, )

    # CMFCore and CMFDefault Tools
    from Products.CMFCore import CachingPolicyManager
    import MembershipTool, WorkflowTool, URLTool, MetadataTool, RegistrationTool, MemberDataTool
    import PropertiesTool, ActionsTool, TypesTool, UndoTool

    # Plone Tools
    import FormulatorTool, PloneTool, NavigationTool, FactoryTool, FormTool, \
           InterfaceTool, MigrationTool, PloneControlPanel

    tools = ( MembershipTool.MembershipTool,
              MemberDataTool.MemberDataTool,
              FormulatorTool.FormulatorTool,
              PloneTool.PloneTool,
              WorkflowTool.WorkflowTool,
              CachingPolicyManager.CachingPolicyManager,
              NavigationTool.NavigationTool,
              FactoryTool.FactoryTool,
              FormTool.FormTool,
              PropertiesTool.PropertiesTool,
              MigrationTool.MigrationTool,
              InterfaceTool.InterfaceTool,
              PloneControlPanel.PloneControlPanel,
              RegistrationTool.RegistrationTool,
              URLTool.URLTool,
              MetadataTool.MetadataTool,
              ActionsTool.ActionsTool,
              TypesTool.TypesTool,
              UndoTool.UndoTool,
            )

    from Products.CMFCore import utils
    import Portal

    z_bases = utils.initializeBasesPhase1(contentClasses, this_module)
    utils.initializeBasesPhase2( z_bases, context )

    utils.ToolInit('Plone Tool', tools=tools,
                   product_name='CMFPlone', icon='tool.gif',
                   ).initialize( context )

    utils.ContentInit( 'Plone Content'
                     , content_types=contentClasses
                     , permission=ADD_CONTENT_PERMISSION
                     , extra_constructors=contentConstructors
                     , fti=ftis
                     ).initialize( context )

    Portal.register(context, cmfplone_globals)

    import CustomizationPolicy
    import PrivateSitePolicy

    CustomizationPolicy.register(context, cmfplone_globals)
    PrivateSitePolicy.register(context, cmfplone_globals)

