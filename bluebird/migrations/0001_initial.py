
from south.db import db
from django.db import models
from bluebird.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'TwitterConsumer'
        db.create_table('bluebird_twitterconsumer', (
            ('id', orm['bluebird.TwitterConsumer:id']),
            ('auth_portal', orm['bluebird.TwitterConsumer:auth_portal']),
            ('key', orm['bluebird.TwitterConsumer:key']),
            ('secret', orm['bluebird.TwitterConsumer:secret']),
        ))
        db.send_create_signal('bluebird', ['TwitterConsumer'])
        
        # Adding model 'TwitterProfile'
        db.create_table('bluebird_twitterprofile', (
            ('id', orm['bluebird.TwitterProfile:id']),
            ('twitter_identification', orm['bluebird.TwitterProfile:twitter_identification']),
            ('raw_data', orm['bluebird.TwitterProfile:raw_data']),
        ))
        db.send_create_signal('bluebird', ['TwitterProfile'])
        
        # Adding model 'TwitterIdentification'
        db.create_table('bluebird_twitteridentification', (
            ('id', orm['bluebird.TwitterIdentification:id']),
            ('user', orm['bluebird.TwitterIdentification:user']),
            ('consumer', orm['bluebird.TwitterIdentification:consumer']),
            ('uid', orm['bluebird.TwitterIdentification:uid']),
            ('key', orm['bluebird.TwitterIdentification:key']),
            ('secret', orm['bluebird.TwitterIdentification:secret']),
        ))
        db.send_create_signal('bluebird', ['TwitterIdentification'])
        
        # Adding ManyToManyField 'TwitterConsumer.sites'
        db.create_table('bluebird_twitterconsumer_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('twitterconsumer', models.ForeignKey(orm.TwitterConsumer, null=False)),
            ('site', models.ForeignKey(orm['sites.Site'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'TwitterConsumer'
        db.delete_table('bluebird_twitterconsumer')
        
        # Deleting model 'TwitterProfile'
        db.delete_table('bluebird_twitterprofile')
        
        # Deleting model 'TwitterIdentification'
        db.delete_table('bluebird_twitteridentification')
        
        # Dropping ManyToManyField 'TwitterConsumer.sites'
        db.delete_table('bluebird_twitterconsumer_sites')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'bluebird.twitterconsumer': {
            'auth_portal': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'twitter_auth_portal'", 'unique': 'True', 'to': "orm['sites.Site']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']"})
        },
        'bluebird.twitteridentification': {
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['bluebird.TwitterConsumer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'twitter_auth'", 'unique': 'True', 'to': "orm['auth.User']"})
        },
        'bluebird.twitterprofile': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'raw_data': ('django.db.models.fields.TextField', [], {}),
            'twitter_identification': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'twitter_profile'", 'unique': 'True', 'to': "orm['bluebird.TwitterIdentification']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['bluebird']
