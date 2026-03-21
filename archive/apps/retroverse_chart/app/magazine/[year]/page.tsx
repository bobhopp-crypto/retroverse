import MagazineYearClient from './MagazineYearClient'

export function generateStaticParams() {
  return Array.from({ length: 2024 - 1958 + 1 }, (_, i) => ({
    year: String(1958 + i),
  }))
}

export default async function MagazineYearPage({
  params,
}: {
  params: Promise<{ year: string }>
}) {
  const { year } = await params
  return <MagazineYearClient year={year} />
}
