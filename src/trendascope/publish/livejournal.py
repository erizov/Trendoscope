"""
LiveJournal publisher using XML-RPC API.
Publish posts directly to LiveJournal blogs.
"""
import xmlrpc.client
from typing import Dict, Any, Optional, List
from datetime import datetime
import time
import logging


logger = logging.getLogger(__name__)


class LiveJournalPublisher:
    """Publish posts directly to LiveJournal."""
    
    def __init__(self, username: str, password: str):
        """
        Initialize LiveJournal publisher.
        
        Args:
            username: LiveJournal username
            password: LiveJournal password
        """
        self.username = username
        self.password = password
        self.server = xmlrpc.client.ServerProxy(
            'https://www.livejournal.com/interface/xmlrpc',
            use_datetime=True
        )
        self._validate_credentials()
    
    def _validate_credentials(self) -> bool:
        """Validate credentials by attempting login."""
        try:
            result = self.server.LJ.XMLRPC.login({
                'username': self.username,
                'password': self.password,
                'ver': 1
            })
            logger.info(f"Successfully authenticated as {self.username}")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def publish_post(
        self,
        title: str,
        text: str,
        tags: Optional[List[str]] = None,
        security: str = "public",
        allow_comments: bool = True,
        schedule_time: Optional[datetime] = None,
        draft: bool = False
    ) -> Dict[str, Any]:
        """
        Publish post to LiveJournal.
        
        Args:
            title: Post title
            text: Post text (HTML or plain text)
            tags: List of tags
            security: Security level (public, private, friends)
            allow_comments: Allow comments
            schedule_time: Schedule for future posting
            draft: Save as draft
        
        Returns:
            {
                'success': True/False,
                'post_url': 'https://...',
                'item_id': 123,
                'error': 'error message' (if failed)
            }
        """
        try:
            # Prepare event structure
            event = {
                'username': self.username,
                'password': self.password,
                'event': text,
                'subject': title,
                'lineendings': 'unix',
                'ver': 1
            }
            
            # Add properties
            props = {
                'opt_nocomments': 0 if allow_comments else 1,
            }
            
            if tags:
                props['taglist'] = ', '.join(tags)
            
            event['props'] = props
            
            # Set security
            if security == 'private':
                event['security'] = 'private'
            elif security == 'friends':
                event['security'] = 'usemask'
                event['allowmask'] = 1
            else:
                event['security'] = 'public'
            
            # Schedule if needed
            if schedule_time:
                event['year'] = schedule_time.year
                event['mon'] = schedule_time.month
                event['day'] = schedule_time.day
                event['hour'] = schedule_time.hour
                event['min'] = schedule_time.minute
            
            # Call LJ API
            logger.info(f"Publishing post: {title[:50]}...")
            response = self.server.LJ.XMLRPC.postevent(event)
            
            # Build URL
            item_id = response.get('itemid', 0)
            anum = response.get('anum', 0)
            
            # LJ URL format: https://username.livejournal.com/ITEMID.html
            # where ITEMID = itemid * 256 + anum
            post_id = item_id * 256 + anum
            post_url = f"https://{self.username}.livejournal.com/{post_id}.html"
            
            logger.info(f"Successfully published: {post_url}")
            
            return {
                'success': True,
                'post_url': post_url,
                'item_id': item_id,
                'anum': anum,
                'post_id': post_id
            }
            
        except xmlrpc.client.Fault as e:
            logger.error(f"XML-RPC Fault: {e.faultCode} - {e.faultString}")
            return {
                'success': False,
                'error': f"LiveJournal error: {e.faultString}"
            }
        except Exception as e:
            logger.error(f"Publishing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def edit_post(
        self,
        item_id: int,
        title: str,
        text: str,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Edit existing post.
        
        Args:
            item_id: Post item ID
            title: New title
            text: New text
            tags: New tags
        
        Returns:
            Success/failure dictionary
        """
        try:
            event = {
                'username': self.username,
                'password': self.password,
                'itemid': item_id,
                'event': text,
                'subject': title,
                'lineendings': 'unix',
                'ver': 1
            }
            
            if tags:
                event['props'] = {
                    'taglist': ', '.join(tags)
                }
            
            response = self.server.LJ.XMLRPC.editevent(event)
            
            logger.info(f"Successfully edited post {item_id}")
            
            return {
                'success': True,
                'item_id': item_id
            }
            
        except Exception as e:
            logger.error(f"Edit failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_post(self, item_id: int) -> Dict[str, Any]:
        """
        Delete post.
        
        Args:
            item_id: Post item ID
        
        Returns:
            Success/failure dictionary
        """
        try:
            event = {
                'username': self.username,
                'password': self.password,
                'itemid': item_id,
                'event': '',
                'ver': 1
            }
            
            self.server.LJ.XMLRPC.editevent(event)
            
            logger.info(f"Successfully deleted post {item_id}")
            
            return {
                'success': True,
                'item_id': item_id
            }
            
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_post(self, item_id: int) -> Optional[Dict[str, Any]]:
        """
        Get post content.
        
        Args:
            item_id: Post item ID
        
        Returns:
            Post dictionary or None
        """
        try:
            request = {
                'username': self.username,
                'password': self.password,
                'selecttype': 'one',
                'itemid': item_id,
                'ver': 1
            }
            
            response = self.server.LJ.XMLRPC.getevents(request)
            
            if response and 'events' in response and response['events']:
                event = response['events'][0]
                return {
                    'item_id': event.get('itemid'),
                    'title': event.get('subject', ''),
                    'text': event.get('event', ''),
                    'url': event.get('url', ''),
                    'time': event.get('eventtime', ''),
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Get post failed: {e}")
            return None
    
    def get_recent_posts(self, count: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent posts.
        
        Args:
            count: Number of posts to retrieve
        
        Returns:
            List of post dictionaries
        """
        try:
            request = {
                'username': self.username,
                'password': self.password,
                'selecttype': 'lastn',
                'howmany': min(count, 50),  # LJ limits to 50
                'ver': 1
            }
            
            response = self.server.LJ.XMLRPC.getevents(request)
            
            posts = []
            if response and 'events' in response:
                for event in response['events']:
                    posts.append({
                        'item_id': event.get('itemid'),
                        'title': event.get('subject', ''),
                        'text': event.get('event', ''),
                        'url': event.get('url', ''),
                        'time': event.get('eventtime', ''),
                    })
            
            return posts
            
        except Exception as e:
            logger.error(f"Get recent posts failed: {e}")
            return []
    
    def test_connection(self) -> bool:
        """
        Test connection to LiveJournal.
        
        Returns:
            True if connection successful
        """
        return self._validate_credentials()


def publish_generated_post(
    generated_post: Dict[str, Any],
    username: str,
    password: str,
    security: str = "public",
    preview: bool = False
) -> Dict[str, Any]:
    """
    Publish a generated post to LiveJournal.
    
    Args:
        generated_post: Post from post_generator.generate_post()
        username: LJ username
        password: LJ password
        security: Security level
        preview: If True, return preview without publishing
    
    Returns:
        Publishing result dictionary
    """
    title = generated_post.get('title', 'Без заголовка')
    text = generated_post.get('text', '')
    tags = generated_post.get('tags', [])
    
    if preview:
        return {
            'success': True,
            'preview': True,
            'title': title,
            'text': text,
            'tags': tags,
            'message': 'Preview mode - post not published'
        }
    
    publisher = LiveJournalPublisher(username, password)
    result = publisher.publish_post(
        title=title,
        text=text,
        tags=tags,
        security=security
    )
    
    return result


def schedule_post(
    generated_post: Dict[str, Any],
    username: str,
    password: str,
    schedule_time: datetime,
    security: str = "public"
) -> Dict[str, Any]:
    """
    Schedule post for future publishing.
    
    Args:
        generated_post: Generated post dictionary
        username: LJ username
        password: LJ password
        schedule_time: When to publish
        security: Security level
    
    Returns:
        Scheduling result
    """
    publisher = LiveJournalPublisher(username, password)
    
    return publisher.publish_post(
        title=generated_post.get('title', ''),
        text=generated_post.get('text', ''),
        tags=generated_post.get('tags', []),
        security=security,
        schedule_time=schedule_time
    )

