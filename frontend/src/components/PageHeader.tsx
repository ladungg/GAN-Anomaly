export default function PageHeader() {
  return (
    <header className="w-full bg-white border-b">
      <div className="max-w-6xl mx-auto py-4 px-4 flex items-center justify-center">
        {/* LOGO */}
        <img
          src="/logo.png"
          alt="Logo Học viện"
          className="w-20 h-20 object-contain mr-5"
        />

        {/* TEXT */}
        <div className="text-center">
          <h1 className="text-2xl font-bold uppercase tracking-wide">
            Học viện Kỹ thuật và Công nghệ An ninh
          </h1>
          <p className="text-base text-gray-600 mt-1">
            Hệ thống phát hiện bất thường dựa trên GAN
          </p>
        </div>
      </div>
    </header>
  );
}
