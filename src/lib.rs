extern crate libc as real_libc;
#[macro_use]
extern crate bitflags;

#[cfg(any(target_os = "linux", target_os = "android"))]
#[path = "platform/linux.rs"]
#[macro_use]
mod platform;

pub use platform::*;

/// A hack to get the macros to work nicely.
#[doc(hidden)]
pub use real_libc as libc;

extern "C" {
    #[doc(hidden)]
    pub fn ioctl(fd: libc::c_int, req: libc::c_ulong, ...) -> libc::c_int;
}

#[cfg(not(any(target_os = "linux", target_os = "android")))]
use platform_not_supported;
