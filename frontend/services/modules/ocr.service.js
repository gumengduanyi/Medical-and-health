import { API_ENDPOINTS } from '@/config/api.config.js'
import { request, uploadFile } from '@/services/request.js'

const OCR_POLL_INTERVAL = 2000
const OCR_MAX_ATTEMPTS = 180

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function getJobUrl(jobId) {
  return API_ENDPOINTS.ocr.job.replace(':id', jobId)
}

async function pollOcrJob(jobId) {
  for (let attempt = 0; attempt < OCR_MAX_ATTEMPTS; attempt += 1) {
    const job = await request({ url: getJobUrl(jobId), method: 'GET' })
    if (job.status === 'succeeded') return job.result
    if (job.status === 'failed') {
      throw new Error(job.error || 'OCR 识别失败')
    }
    await sleep(OCR_POLL_INTERVAL)
  }
  throw new Error('OCR 识别超时，请稍后重试')
}

async function submitAndWait(url, filePath, formData = {}) {
  const job = await uploadFile({ url, filePath, formData })
  if (!job.jobId) return job
  return pollOcrJob(job.jobId)
}

export function scanReport(filePath, formData = {}) {
  return submitAndWait(API_ENDPOINTS.ocr.scanReport, filePath, formData)
}

export function scanMedicine(filePath, formData = {}) {
  return submitAndWait(API_ENDPOINTS.ocr.scanMedicine, filePath, formData)
}

export function confirmOcrResult(data) {
  return request({
    url: API_ENDPOINTS.ocr.confirm,
    method: 'POST',
    data
  })
}
