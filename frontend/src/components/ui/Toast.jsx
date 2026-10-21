
import { useSyncExternalStore } from 'react'
import {
  dismissToast,
  getToasts,
  subscribeToToasts,
} from './toastStore'

export function ToastStack() {
  const items = useSyncExternalStore(
    subscribeToToasts,
    getToasts,
    getToasts,
  )

  return (
    <div className="cl-toast-stack" role="status" aria-live="polite">
      {items.map((item) => (
        <div
          key={item.id}
          className={`cl-toast ${
            item.type === 'error' ? 'cl-toast--error' : ''
          }`}
          onClick={() => dismissToast(item.id)}
        >
          {item.message}
        </div>
      ))}
    </div>
  )
}
