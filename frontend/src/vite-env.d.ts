// CSS Modules type declarations
declare module '*.module.css' {
  const classes: Record<string, string>
  export default classes
}

// Vite env type augmentation
interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly MODE: string
  readonly DEV: boolean
  readonly PROD: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
