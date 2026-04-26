import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes, type ReactNode } from 'react'
import styles from './FloatingInput.module.css'

interface BaseProps {
  label: string
  error?: string
  helper?: string
  iconRight?: ReactNode
}

type InputProps = BaseProps &
  Omit<InputHTMLAttributes<HTMLInputElement>, 'placeholder'> & {
    multiline?: false
  }

type TextareaProps = BaseProps &
  Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'placeholder'> & {
    multiline: true
  }

type FloatingInputProps = InputProps | TextareaProps

const FloatingInput = forwardRef<HTMLInputElement | HTMLTextAreaElement, FloatingInputProps>(
  ({ label, error, helper, iconRight, className, multiline, ...rest }, ref) => {
    const fieldClass = [
      styles.field,
      multiline ? styles.textarea : '',
      error ? styles.error : '',
      iconRight ? styles.withIconRight : '',
      className ?? '',
    ]
      .filter(Boolean)
      .join(' ')

    const id = (rest as { id?: string }).id ?? label.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className={styles.wrapper}>
        {multiline ? (
          <textarea
            id={id}
            className={fieldClass}
            placeholder=" "
            ref={ref as React.Ref<HTMLTextAreaElement>}
            {...(rest as TextareaHTMLAttributes<HTMLTextAreaElement>)}
          />
        ) : (
          <input
            id={id}
            className={fieldClass}
            placeholder=" "
            ref={ref as React.Ref<HTMLInputElement>}
            {...(rest as InputHTMLAttributes<HTMLInputElement>)}
          />
        )}
        <label className={styles.label} htmlFor={id}>
          {label}
        </label>
        {iconRight && <span className={styles.iconRight}>{iconRight}</span>}
        {(helper || error) && (
          <span className={`${styles.helper} ${error ? styles.errorText : ''}`}>
            {error ?? helper}
          </span>
        )}
      </div>
    )
  }
)

FloatingInput.displayName = 'FloatingInput'
export default FloatingInput
