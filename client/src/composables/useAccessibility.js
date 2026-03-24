import { reactive, computed } from "vue"

const accessibility = reactive({
    isOpen: false,
    textSize: Number(localStorage.getItem("textSize")) || 100,
    useDyslexicFont: localStorage.getItem("useDyslexicFont") === "true",
    colorMode: localStorage.getItem("colorMode") || "normal",
    darkMode: localStorage.getItem("darkMode") === "true"
})

if (accessibility.darkMode) {
    document.documentElement.classList.add("dark")
} else {
    document.documentElement.classList.remove("dark")
}

function openAccessibility() {
    accessibility.isOpen = true
}

function closeAccessibility() {
    accessibility.isOpen = false
    saveAccessibility()
}

function toggleAccessibility() {
    accessibility.isOpen = !accessibility.isOpen
    if (!accessibility.isOpen) {
        saveAccessibility()
    }
}

function toggleDarkMode() {
    accessibility.darkMode = !accessibility.darkMode
    if (accessibility.darkMode) {
        document.documentElement.classList.add("dark")
    } else {
        document.documentElement.classList.remove("dark")
    }
    saveAccessibility()
}

function saveAccessibility() {
    localStorage.setItem("textSize", accessibility.textSize)
    localStorage.setItem("useDyslexicFont", accessibility.useDyslexicFont)
    localStorage.setItem("colorMode", accessibility.colorMode)
    localStorage.setItem("darkMode", accessibility.darkMode)
}

const appStyle = computed(() => ({
    fontSize: `${accessibility.textSize}%`,
    fontFamily: accessibility.useDyslexicFont
        ? "'OpenDyslexic', Arial"
        : "'Montserrat', sans-serif"
}))

const appClasses = computed(() => [
    `color-${accessibility.colorMode}`
])

export function useAccessibility() {
    return {
        accessibility,
        openAccessibility,
        closeAccessibility,
        toggleAccessibility,
        saveAccessibility,
        toggleDarkMode,
        appStyle,
        appClasses
    }
}
