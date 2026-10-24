let toasts = []
let nextId = 0

const listeners = new Set()
const timers = new Map()

function emit() {
    listeners.forEach((listener) => listener())
}

export function dismissToast(id) {
    clearTimeout(timers.get(id))
    timers.delete(id)

    toasts = toasts.filter((item) => item.id !== id)
    emit()
}

function push(message, type = 'success', duration = 3800) {
    const id = ++nextId

    toasts = [...toasts.slice(-3), { id, message, type }]

    timers.set(
        id,
        setTimeout(() => dismissToast(id), duration),
    )

    emit()
}

export const toast = {
    success: (message, duration) => push(message, 'success', duration),
    error: (message, duration) => push(message, 'error', duration),
}

export function subscribeToToasts(listener) {
    listeners.add(listener)

    return () => listeners.delete(listener)
}

export function getToasts() {
    return toasts
}