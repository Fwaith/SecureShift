import { reactive, computed } from "vue"

const accessibility = reactive({
    isOpen: false,
    textSize: Number(localStorage.getItem("textSize")) || 100,
    useDyslexicFont: localStorage.getItem("useDyslexicFont") === "true",
    colorMode: localStorage.getItem("colorMode") || "normal"
})

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

function saveAccessibility() {
    localStorage.setItem("textSize", accessibility.textSize)
    localStorage.setItem("useDyslexicFont", accessibility.useDyslexicFont)
    localStorage.setItem("colorMode", accessibility.colorMode)
}

const appStyle = computed(() => ({
    fontSize: `${accessibility.textSize}%`,
    fontFamily: accessibility.useDyslexicFont
        ? "Arial, Verdana, sans-serif"
        : "system-ui, sans-serif"
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
        appStyle,
        appClasses
    }
}
