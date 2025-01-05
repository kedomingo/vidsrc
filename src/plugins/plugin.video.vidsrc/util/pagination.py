import xbmcgui
import xbmcplugin

from util.util import build_url, append_dicts


def previous_pages(ADDON_HANDLE, ADDON_BASE_URL, page, params):
  page = int(page)
  main_url = build_url({}, ADDON_BASE_URL)
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, main_url,
                              xbmcgui.ListItem('BACK TO MAIN PAGE'), True)

  if page > 1:
    prev_url = build_url(
        append_dicts(params, {'page': 1}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem('First'), True)

  if page > 10:
    prev_url = build_url(
        append_dicts(params, {'page': page - 10}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 10}'), True)

  if page > 2:
    prev_url = build_url(
        append_dicts(params, {'page': page - 1}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 1}'), True)


def next_pages(ADDON_HANDLE, ADDON_BASE_URL, page, total_pages, params):
  page = int(page)
  if page < total_pages:
    next_url = build_url(
        append_dicts(params, {'page': page + 1}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 1}'), True)

  if page + 2 < total_pages:
    next_url = build_url(
        append_dicts(params, {'page': page + 2}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 2}'), True)

  if page + 5 < total_pages:
    next_url = build_url(
        append_dicts(params, {'page': page + 5}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 5}'), True)

  if page + 1 < total_pages:
    next_url = build_url(
        append_dicts(params, {'page': total_pages - 1}),
        ADDON_BASE_URL
    )
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem('Last'), True)
