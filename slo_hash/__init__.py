r"""
A ``GET`` request to the manifest object will return the concatenation of the
objects from the manifest much like DLO. If query url with
``multipart-manifest=get`` thus extra metadata ``X-Object-Meta-SLOmd5``
with md5sum of SLO object will be added in SLO manifest object.
===================== ==================================================
Header                Value
===================== ==================================================
X-Object-Meta-SLOmd5  md5sum of whole segments, md5 of SLO object
"""
import io
import json
import hashlib
from swift.common.http import is_success
from swiftclient.client import Connection
from swiftclient import exceptions as client_exceptions
from swift.common.utils import split_path, get_logger, closing_if_possible, \
    get_valid_utf8_str, split_path
from swift.common.wsgi import WSGIContext, make_subrequest, make_pre_authed_request
from swift.common.utils import FileLikeIter
from swift.common.exceptions import ListingIterError, SegmentError
from webob import Request
from webob.exc import HTTPBadRequest, HTTPServerError

class SLOHashMiddleware(WSGIContext):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='slo_hash')

    def __call__(self, env, start_response):
        req = Request(env)
        # when HTTP GET only
        if env['REQUEST_METHOD'] not in ['GET']:
            return self.app(env, start_response)

        version, account, container, obj = split_path(
            env['PATH_INFO'], 1, 4, True)

        ### resp = self._app_call(env) ###
        try:
            resp = self._app_call(env)
        except Exception:
            resp = HTTPServerError(request=req, body="error")
            return resp(env, start_response)
        status = int(self._response_status.split()[0])

        if status < 200 or status > 300:
            start_response(self._response_status, self._response_headers,
                           self._response_exc_info)
            return resp
        SLOmd5= ''
        if req.params.get('multipart-manifest') == 'get':
            if req.params.get('format') == 'raw':
                resp = self.convert_segment_listing(
                    self._response_headers, resp)
            else:
                h = hashlib.md5()
                segments = self._get_manifest_read(resp)
                for seg_dict in segments:
                    if 'data' in seg_dict:
                        continue
                    sub_path = get_valid_utf8_str(seg_dict['name'])
                    sub_cont, sub_obj = split_path(sub_path, 2, 2, True)
                    h.update(self._fetch_sub_slo_segments(req, version,
                             account, sub_cont, sub_obj))
                SLOmd5 = h.hexdigest()
                #new_headers = []
                #for header, value in self._response_headers:
                #    if header == 'X-Static-Large-Object' \
                #       and value == 'True':
                #        new_headers.append(('X-Object-Meta-SLOmd5',
                #                            SLOmd5))
                #    new_headers.append((header, value))
                #self._response_headers = new_headers
            start_response(self._response_status,
                           self._response_headers,
                           self._response_exc_info)
            headers = {}
            headers['X-Object-Meta-SLOmd5'] = SLOmd5
            #self.logger.info(headers)
            post_req = make_pre_authed_request(env, method='POST',
                                               swift_source='SLOmd5',
                                               path=env['PATH_INFO'],
                                               headers=headers)
            post_resp = post_req.get_response(self.app)
            if not is_success(post_resp.status_int):
                self.logger.info('POST with SLOmd5 headers failed: ' +
                                 str(post_resp.body))
            return self.app(env, start_response)

    def _get_manifest_read(self, resp_iter):
        with closing_if_possible(resp_iter):
            resp_body = ''.join(resp_iter)
        try:
            segments = json.loads(resp_body)
        except ValueError:
            segments = []

        return segments


    def _fetch_sub_slo_segments(self, req, version, acc, con, obj):
        """
        Fetch the submanifest, parse it, and return it.
        Raise exception on failures.
        """
        sub_req = make_subrequest(
            req.environ, path='/'.join(['', version, acc, con, obj]),
            method='GET',
            headers={'x-auth-token': req.headers.get('x-auth-token')},
            agent='%(orig)s SLO MultipartGET', swift_source='SLO')
        sub_resp = sub_req.get_response(self.app)

        if not sub_resp.is_success:
            close_if_possible(sub_resp.app_iter)
            raise ListingIterError(
                'while fetching %s, GET of submanifest %s '
                'failed with status %d' % (req.path, sub_req.path,
                                           sub_resp.status_int))
        try:
            with closing_if_possible(sub_resp.app_iter):
                return ''.join(sub_resp.app_iter)
        except ValueError as err:
            raise ListingIterError(
                'while fetching %s, String-decoding of submanifest %s '
                'failed with %s' % (req.path, sub_req.path, err))

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def slo_hash(app):
        return SLOHashMiddleware(app, conf)

    return slo_hash
