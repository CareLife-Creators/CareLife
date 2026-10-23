import { forwardRef } from 'react'

/**
 * CareLife shared button.
 * Variants: primary | ghost | soft | danger   Sizes: sm | md | lg
 * Shows a spinner automatically when `loading` is true and disables the button.
 */
const Button = forwardRef(function Button(
  { variant = 'primary', size = 'md', block = false, loading = false, icon = null, children, className = '', ...rest },
  ref
) {
  const classes = [
    'cl-btn',
    `cl-btn--${variant}`,
    size !== 'md' ? `cl-btn--${size}` : '',
    block ? 'cl-btn--block' : '',
    className,
  ].filter(Boolean).join(' ')

  return (
    <button ref={ref} className={classes} disabled={loading || rest.disabled} {...rest}>
      {loading ? <span className="cl-spinner" aria-hidden="true" /> : icon}
      {children}
    </button>
  )
})

export default Button