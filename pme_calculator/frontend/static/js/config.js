/**
 * Configuration for API endpoints
 */

export const API_BASE = 
    (window.API_BASE) ?? 
    `${location.protocol}//${location.hostname}${location.port ? ':'+location.port : ''}`; 