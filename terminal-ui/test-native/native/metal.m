#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#include <stdbool.h>
#include <stdint.h>

// Benchmark-only bridge: creates a target and reads Metal's allocation counter.
@interface TerminalMetalProbe : NSObject
@property(nonatomic, strong) id<MTLDevice> device;
@property(nonatomic, strong) id<MTLCommandQueue> queue;
@property(nonatomic, strong) id<MTLTexture> texture;
@property(nonatomic) uint64_t baseline;
@end
@implementation TerminalMetalProbe
@end

void terminal_test_metal_pool(int32_t (*callback)(void *), void *context) {
  @autoreleasepool {
    callback(context);
  }
}

void *terminal_test_metal_create(int32_t width, int32_t height) {
  @autoreleasepool {
    @try {
      TerminalMetalProbe *probe = [TerminalMetalProbe new];
      probe.device = MTLCreateSystemDefaultDevice();
      probe.queue = [probe.device newCommandQueue];
      probe.baseline = probe.device.currentAllocatedSize;
      MTLTextureDescriptor *descriptor = [MTLTextureDescriptor
          texture2DDescriptorWithPixelFormat:MTLPixelFormatBGRA8Unorm
                                       width:(NSUInteger)width
                                      height:(NSUInteger)height
                                   mipmapped:NO];
      descriptor.usage = MTLTextureUsageRenderTarget | MTLTextureUsageShaderRead;
      descriptor.storageMode = MTLStorageModePrivate;
      probe.texture = [probe.device newTextureWithDescriptor:descriptor];
      return probe.device && probe.queue && probe.texture
                 ? (__bridge_retained void *)probe
                 : NULL;
    } @catch (NSException *exception) {
      return NULL;
    }
  }
}

void *terminal_test_metal_object(void *pointer, int32_t kind) {
  TerminalMetalProbe *probe = (__bridge TerminalMetalProbe *)pointer;
  switch (kind) {
  case 0:
    return (__bridge void *)probe.device;
  case 1:
    return (__bridge void *)probe.queue;
  default:
    return (__bridge void *)probe.texture;
  }
}

uint64_t terminal_test_metal_bytes(void *pointer, bool baseline) {
  TerminalMetalProbe *probe = (__bridge TerminalMetalProbe *)pointer;
  return baseline ? probe.baseline : probe.device.currentAllocatedSize;
}

void terminal_test_metal_release_target(void *pointer) {
  TerminalMetalProbe *probe = (__bridge TerminalMetalProbe *)pointer;
  probe.texture = nil;
}

void terminal_test_metal_close(void *pointer) {
  TerminalMetalProbe *probe = (__bridge_transfer TerminalMetalProbe *)pointer;
  (void)probe;
}
