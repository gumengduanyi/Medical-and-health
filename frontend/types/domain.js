// 数据结构约定，便于后续对接后端接口。

export const HealthProfileShape = {
  id: '',
  name: '',
  sex: '',
  age: 0,
  height: 0,
  weight: 0,
  allergy: '',
  disease: '',
  familyHistory: '',
  geneticHistory: '',
  disableInfo: ''
}

export const MedicineShape = {
  id: '',
  name: '',
  dose: '',
  stock: 0,
  expire: '',
  risk: ''
}

export const OcrResultShape = {
  id: '',
  sourceType: '',
  confidence: 0,
  fields: []
}

export const AiMessageShape = {
  role: 'user',
  content: '',
  createdAt: ''
}
