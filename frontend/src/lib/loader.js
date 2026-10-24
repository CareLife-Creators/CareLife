const LOADER_KEY = 'carelife_loader_seen'

export function shouldShowLoader() {
  try {
    return window.sessionStorage.getItem(LOADER_KEY) !== '1'
  } catch {
    return false
  }
}

export function markLoaderSeen() {
  try {
    window.sessionStorage.setItem(LOADER_KEY, '1')
  } catch {
    // A blocked session store should not stop the page from opening.
  }
}
