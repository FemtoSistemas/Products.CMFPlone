## Script (Python) "image_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=precondition='', field_file='', field_id='', title=None, description=None
##title=Edit an image
##
qst='portal_status_message=Image+changed.'
REQUEST=context.REQUEST
file=field_file
id=field_id

context.edit(
     precondition=precondition,
     file=file)

errors=context.validate_image_edit()
if errors:
    form=getattr( context, context.getTypeInfo().getActionById( 'edit' ) )
    return form()

filename=file.filename
if filename and context.isIDAutoGenerated(id):
    if filename.find('\\') > -1:       
        id=filename.split('\\')[-1]
    else:
        id=filename.split('/')[-1]
        
if not context.isIDAutoGenerated(id): 
    context.REQUEST.set('id', id)

if hasattr(context, 'extended_edit'):
    REQUEST.set('portal_status_message', 'Image+changed.')
    edit_hook=getattr(context,'extended_edit')
    response=edit_hook(redirect=0)
    if response:
        return response

context.rename_object(redirect=0, id=id)

target_action = context.getTypeInfo().getActionById( 'view' )
context.REQUEST.RESPONSE.redirect( '%s/%s?%s' % ( context.absolute_url()
                                                , target_action
                                                , qst
                                                ) )
