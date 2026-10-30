// Vyřízne hlavní objekt (auto) z fotky pomocí Vision, zakryje SPZ a složí čtvercovou ikonu na barevné pozadí.
import Foundation
import Vision
import CoreImage
import CoreImage.CIFilterBuiltins
import AppKit

let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1]), output = URL(fileURLWithPath: args[2])
// SPZ v souřadnicích zdrojové fotky (x, y od horního okraje, šířka, výška)
let plate = CGRect(x: 248, y: 578, width: 280, height: 74)

let ci = CIImage(contentsOf: input)!
let handler = VNImageRequestHandler(ciImage: ci)
let req = VNGenerateForegroundInstanceMaskRequest()
try handler.perform([req])
guard let obs = req.results?.first else { fatalError("objekt nenalezen") }
let maskBuf = try obs.generateScaledMaskForImage(forInstances: obs.allInstances, from: handler)
let mask = CIImage(cvPixelBuffer: maskBuf)

let H = ci.extent.height
// zakrytí SPZ: neutrální šedobílá plocha se zaoblením
let plateRect = CGRect(x: plate.minX, y: H - plate.maxY, width: plate.width, height: plate.height)
let plateFill = CIImage(color: CIColor(red: 0.93, green: 0.94, blue: 0.95)).cropped(to: plateRect)
let car = plateFill.composited(over: ci)

let cut = car.applyingFilter("CIBlendWithMask", parameters: [kCIInputBackgroundImageKey: CIImage.empty(), kCIInputMaskImageKey: mask])
// ořez kolem auta (bbox masky) do čtverce s okrajem
let bbox = obs.allInstances.isEmpty ? ci.extent : cut.extent
var alphaBox = CGRect.null
do {
  let ctx = CIContext()
  let cg = ctx.createCGImage(mask, from: mask.extent)!
  let w = cg.width, h = cg.height
  var px = [UInt8](repeating: 0, count: w * h)
  let cs = CGColorSpaceCreateDeviceGray()
  let bctx = CGContext(data: &px, width: w, height: h, bitsPerComponent: 8, bytesPerRow: w, space: cs, bitmapInfo: 0)!
  bctx.draw(cg, in: CGRect(x: 0, y: 0, width: w, height: h))
  var minX = w, minY = h, maxX = 0, maxY = 0
  for y in 0..<h { for x in 0..<w where px[y * w + x] > 128 { minX = min(minX, x); maxX = max(maxX, x); minY = min(minY, y); maxY = max(maxY, y) } }
  // CGContext má počátek dole → převod na CI souřadnice (také dole)
  alphaBox = CGRect(x: minX, y: minY, width: maxX - minX, height: maxY - minY)
}
_ = bbox
let side = max(alphaBox.width, alphaBox.height) * 1.12
let sq = CGRect(x: alphaBox.midX - side / 2, y: alphaBox.midY - side / 2, width: side, height: side)

// pozadí: tyrkysový přechod v barvách aplikace
let grad = CIFilter.linearGradient()
grad.point0 = CGPoint(x: sq.minX, y: sq.maxY); grad.point1 = CGPoint(x: sq.maxX, y: sq.minY)
grad.color0 = CIColor(red: 0.08, green: 0.55, blue: 0.50); grad.color1 = CIColor(red: 0.02, green: 0.25, blue: 0.24)
let bg = grad.outputImage!.cropped(to: sq)
let composed = cut.composited(over: bg).cropped(to: sq)

let out = composed.transformed(by: CGAffineTransform(translationX: -sq.minX, y: -sq.minY))
  .transformed(by: CGAffineTransform(scaleX: 1024 / side, y: 1024 / side))
let ctx = CIContext()
try ctx.writePNGRepresentation(of: out, to: output, format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
print("ok", Int(alphaBox.width), Int(alphaBox.height))
