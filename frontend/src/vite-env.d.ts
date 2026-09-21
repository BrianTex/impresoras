/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_URL?: string;
    readonly VITE_APP_NAME?: string;
    readonly VITE_LOW_TONER_THRESHOLD?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}
